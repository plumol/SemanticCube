# query.py
import pymongo
import sys
from dotenv import load_dotenv
import os
from meta_ai_api import MetaAI

load_dotenv()
uri = os.getenv("MONGODB_URI")

try:
    client = pymongo.MongoClient(uri)
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except pymongo.errors.ConfigurationError as e:
    print(e)
    print("Invalid URI host error. Check your connection string.")
    sys.exit(1)

db = client.paperDatabase
cube_collection = db["semantic_cube"]
rollup_cache = db["rollup_cache"]  # new collection for cached roll-up summaries


def naive_aggregated_summary_from_text(text):
    return text  # fallback if LLM fails


def generate_rollup_summary(combined_text):
    # print("combined_text:", combined_text)
    prompt = (
        "You are an expert computer science research assistant. "
        "You are provided with one or more aggregated summaries of research paper abstracts. "
        "Even if these summaries come from different sets of papers, your task is to ignore their individual groupings "
        "and produce one unified, coherent summary that captures the overall research themes, methodologies, significant findings, "
        "and emerging trends for the entire collection. "
        "\n\nAggregated Abstracts:\n\n"
        f"{combined_text}\n\n"
        "Unified Summary:"
    )
    try:
        ai_client = MetaAI()
        response = ai_client.prompt(prompt)
        summary = response.get("message", "").strip()
        if not summary:
            return naive_aggregated_summary_from_text(combined_text)
        return summary
    except Exception as e:
        print(f"Error generating rollup summary: {e}")
        return naive_aggregated_summary_from_text(combined_text)


def make_cache_key(category, start_year, start_month, end_year, end_month):
    return f"{category}_{start_year}_{start_month}_{end_year}_{end_month}"


def run_pipeline(
    category=None, start_year=None, start_month=None, end_year=None, end_month=None
):
    from datetime import datetime, timezone

    # Compute the cache key
    cache_key = make_cache_key(category, start_year, start_month, end_year, end_month)

    # First check if there's a cached roll-up for these parameters:
    cached = rollup_cache.find_one({"cache_key": cache_key})
    if cached:
        print("Returning cached roll-up summary.")
        return cached  # Return the cached document

    match_stage = {}
    if category:
        match_stage["category"] = category

    # Try to apply composite filtering when all date parts are provided.
    composite_filter_used = False
    try:
        if (
            start_year is not None
            and start_month is not None
            and end_year is not None
            and end_month is not None
        ):
            # Calculate composite values for the provided date range.
            start_val = int(start_year) * 100 + int(start_month)
            end_val = int(end_year) * 100 + int(end_month)

            # Use $expr to compare the document's composite date field against the range.
            match_stage["$expr"] = {
                "$and": [
                    {
                        "$gte": [
                            {"$add": [{"$multiply": ["$year", 100]}, "$month"]},
                            start_val,
                        ]
                    },
                    {
                        "$lte": [
                            {"$add": [{"$multiply": ["$year", 100]}, "$month"]},
                            end_val,
                        ]
                    },
                ]
            }
            composite_filter_used = True
    except ValueError:
        print("Invalid input for year or month. They must be numbers.")
        return {}

    # Fallback: if the full composite range wasn't provided, use the original separate filters.
    if not composite_filter_used:
        if start_year or end_year:
            year_filter = {}
            if start_year:
                try:
                    year_filter["$gte"] = int(start_year)
                except ValueError:
                    print("Invalid start year. It should be a number.")
                    return {}
            if end_year:
                try:
                    year_filter["$lte"] = int(end_year)
                except ValueError:
                    print("Invalid end year. It should be a number.")
                    return {}
            if year_filter:
                match_stage["year"] = year_filter

        if start_month or end_month:
            month_filter = {}
            if start_month:
                try:
                    month_filter["$gte"] = int(start_month)
                except ValueError:
                    print("Invalid start month. It should be a number.")
                    return {}
            if end_month:
                try:
                    month_filter["$lte"] = int(end_month)
                except ValueError:
                    print("Invalid end month. It should be a number.")
                    return {}
            if month_filter:
                match_stage["month"] = month_filter

    pipeline = []
    if match_stage:
        pipeline.append({"$match": match_stage})

    # Grouping stage to aggregate data from the matched documents.
    pipeline.append(
        {
            "$group": {
                "_id": None,
                "categories": {"$push": "$category"},
                "total_papers": {"$sum": "$paper_count"},
                "paper_ids": {"$push": "$paper_ids"},
                "paper_titles": {"$push": "$paper_titles"},
                "summaries": {"$push": "$aggregated_summary"},
            }
        }
    )

    results = list(cube_collection.aggregate(pipeline))
    if not results:
        return {}

    result_doc = results[0]
    base_summaries = result_doc.get("summaries", [])
    combined_text = "\n\n".join(base_summaries)
    rollup_summary = generate_rollup_summary(combined_text)

    # Prepare the cached document, now also storing the paper_ids
    cache_doc = {
        "cache_key": cache_key,
        "category": category,
        "start_year": int(start_year) if start_year is not None else None,
        "end_year": int(end_year) if end_year is not None else None,
        "start_month": int(start_month) if start_month is not None else None,
        "end_month": int(end_month) if end_month is not None else None,
        "total_papers": result_doc.get("total_papers", 0),
        "paper_ids": result_doc.get("paper_ids", []),
        "rolled_up_summary": rollup_summary,
        "cached_at": datetime.now(timezone.utc),
    }
    # Insert the new cached roll-up document.
    rollup_cache.insert_one(cache_doc)
    result_doc["rolled_up_summary"] = rollup_summary
    return result_doc


if __name__ == "__main__":
    # For testing purposes (adjust these parameters as needed)
    test_params = {
        "category": "cs.AI",
        "start_year": 2023,
        "start_month": 11,
        "end_year": 2024,
        "end_month": 2,
    }
    res = run_pipeline(
        test_params["category"],
        test_params["start_year"],
        test_params["start_month"],
        test_params["end_year"],
        test_params["end_month"],
    )
    print("Query Result:")
    if res:
        print("categories:", res.get("categories"))
        print("total_papers:", res.get("total_papers"))
        print("paper_ids:", res.get("paper_ids"))
        print("paper_titles:", res.get("paper_titles"))
        print("summaries:", res.get("summaries"))
        print("------------------")
        print("rolled_up_summary:", res.get("rolled_up_summary"))
    else:
        print("No results found.")
