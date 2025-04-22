# filter.py
import pymongo
import sys
from dotenv import load_dotenv
import os
from meta_ai_api import MetaAI
from backend.utils.meta_ai import parse_query_to_params

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

def run_filter_pipeline(query_text: str):
    """
    Run the filtering pipeline based on natural language query
    Similar structure to run_pipeline in query.py but returns individual papers
    """
    try:
        # Use the existing LLM parser to extract parameters
        params = parse_query_to_params(query_text)
        
        match_stage = {}
        
        # Add category if present
        if params.get("category"):
            match_stage["category"] = params["category"]
        
        # Try to apply composite filtering for date range
        try:
            start_val = int(params["start_year"]) * 100 + int(params["start_month"])
            end_val = int(params["end_year"]) * 100 + int(params["end_month"])

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
        except (ValueError, TypeError) as e:
            print(f"Error creating date filter: {e}")
            return {}

        pipeline = []
        if match_stage:
            pipeline.append({"$match": match_stage})

        # Project only the fields we need
        pipeline.append({
            "$project": {
                "title": 1,
                "paper_ids": 1,
                "paper_titles": 1,
                "category": 1,
                "year": 1,
                "month": 1,
                "aggregated_summary": 1
            }
        })

        results = list(cube_collection.aggregate(pipeline))
        if not results:
            return {
                "papers": [],
                "total_count": 0
            }

        # Format the results
        formatted_papers = []
        for result in results:
            # Handle potentially nested paper_ids and paper_titles
            paper_ids = result.get("paper_ids", [])
            paper_titles = result.get("paper_titles", [])
            
            if isinstance(paper_ids, list) and isinstance(paper_titles, list):
                # If we have matching paper_ids and titles, create individual entries
                for pid, title in zip(paper_ids, paper_titles):
                    formatted_papers.append({
                        "paper_id": pid,
                        "title": title,
                        "category": result.get("category"),
                        "year": result.get("year"),
                        "month": result.get("month"),
                        "summary": result.get("aggregated_summary", "")
                    })
            else:
                # Fallback for single paper entries
                formatted_papers.append({
                    "paper_id": result.get("paper_ids"),
                    "title": result.get("paper_titles"),
                    "category": result.get("category"),
                    "year": result.get("year"),
                    "month": result.get("month"),
                    "summary": result.get("aggregated_summary", "")
                })

        return {
            "papers": formatted_papers,
            "total_count": len(formatted_papers)
        }

    except Exception as e:
        print(f"Error in filter pipeline: {e}")
        return {
            "papers": [],
            "total_count": 0
        }

if __name__ == "__main__":
    test_queries = [
        "Show me AI papers from March 2024",
        "Machine learning papers from January to March 2024",
        "Recent computer vision research",
        "NLP papers from last year",
        "Robotics papers in 2024",
        "Security papers from February 2024",
    ]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        print("-" * 50)
        
        res = run_filter_pipeline(query)
        if res["papers"]:
            print(f"Found {res['total_count']} papers:")
            for i, paper in enumerate(res["papers"], 1):
                print(f"\n{i}. Title: {paper['title']}")
                print(f"   Category: {paper['category']}")
                print(f"   Date: {paper['year']}/{paper['month']}")
                print(f"   Summary: {paper['summary'][:200]}...")
        else:
            print("No papers found.")
        
        print("\n" + "=" * 50)