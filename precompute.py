import pymongo
import sys
import csv
from collections import defaultdict
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGODB_URI")
csv_file_path = "clean_fields_filter_date_sample50.csv"

# connect to mongo
try:
    client = pymongo.MongoClient(uri)
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except pymongo.errors.ConfigurationError:
    print(e)
    sys.exit(1)


db = client.paperDatabase
papers_collection = db["papers"]
cube_collection = db["semantic_cube"]

# Clear out old data
cube_collection.delete_many({})
papers_collection.delete_many({})

# Dictionary to hold aggregated data
# Key: (year, category) -> Value: list of rows (papers)
aggregator = defaultdict(list)

with open(csv_file_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # 1) Parse the update_date as a datetime
        date_str = row["update_date"]  # e.g., "2022-10-17"
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        year = date_obj.year
        month = date_obj.month

        # 2) Extract all cs categories (e.g., "cs.PL cs.CY" becomes a list)
        categories = row["cs_categories"].split()

        # 3.1) Group by (year, month, category) for each category the paper belongs to
        for cat in categories:
            aggregator[(year, month, cat)].append(row)

        # 3.2) Build a document for the individual paper, storing all categories
        paper_doc = {
            "id": row["id"],
            "title": row["title"],
            "abstract": row["abstract"],
            "categories": categories,  # store the complete list of categories
            "year": year,
            "month": month
            # Add more fields if needed
        }
        papers_collection.insert_one(paper_doc)


def naive_aggregated_summary(papers):
    # Just concatenate abstracts
    # Or you could pick the top 3 sentences from each abstract, etc.
    all_abstracts = [p["abstract"] for p in papers]
    return " ".join(all_abstracts)


# Choose summary function
summary_function = naive_aggregated_summary  # or llm_aggregated_summary


# cube_collection.insert_one({"year":2000, "name":"Sabrina"})
for (year, month, category), papers in aggregator.items():
    # Compute aggregates
    count = len(papers)
    summary = summary_function(papers)
    paper_ids = [p["id"] for p in papers]

    # Build the document
    doc = {
        "year": year,
        "month": month,
        "category": category,
        "paper_count": count,
        "aggregated_summary": summary,
        "paper_ids": paper_ids,
        # Optional: store additional metadata, timestamps, etc.
    }
    try:
        # Insert into MongoDB
        cube_collection.insert_one(doc)
    except pymongo.errors.OperationFailure:
        sys.exit(1)
    else:
        pass
        # print("doc inserted")