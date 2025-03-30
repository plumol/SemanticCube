import pymongo
import openllm
import openai
from openai import OpenAI
from meta_ai_api import MetaAI
import sys
import csv
from collections import defaultdict
import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
uri = os.getenv("MONGODB_URI")
csv_file_path = "dataset/clean_fields_filter_date_sample50.csv"

# Updated category map based on your dataset (for roll-up)
category_map = {
    # AI & ML
    "cs.LG": "AI",
    "cs.AI": "AI",
    "cs.CL": "AI",
    "cs.CV": "AI",
    "cs.NE": "AI",
    "cs.RO": "AI",

    # Security & Privacy
    "cs.CR": "Security",

    # Systems
    "cs.DC": "Systems",
    "cs.NI": "Systems",
    "cs.SE": "Systems",
    "cs.SY": "Systems",
    "cs.DS": "Systems",

    # Human Factors
    "cs.HC": "Human-Computer Interaction",
    "cs.CY": "Human-Computer Interaction",

    # Theory & Foundations
    "cs.IT": "Theory",
    "cs.NA": "Theory",
    "cs.ET": "Theory",

    # Signal & Vision
    "cs.SI": "Signal Processing",
    "cs.SD": "Signal Processing",

    # Hardware / Embedded
    "cs.CE": "Hardware",
    "cs.CC": "Hardware",

    # Digital Libraries
    "cs.DL": "Digital Libraries",
}

# Extract techniques using basic keyword matching (for drill-down & slide/dice) replace this with llm extraction later
def extract_techniques(text):
    keywords = ["transformer", "bert", "gpt", "attention", "resnet", "diffusion"]
    text = text.lower()
    return [k.upper() if k.startswith("gpt") or k == "bert" else k.capitalize() for k in keywords if k in text]

# Connect to MongoDB
try:
    client = pymongo.MongoClient(uri)
    print("Pinged your deployment. You successfully connected to MongoDB!")
    client.admin.command('ping')
except pymongo.errors.ConfigurationError as e:
    print(e)
    sys.exit(1)

# Select database and collections
db = client.paperDatabase
papers_collection = db["papers"]
cube_collection = db["semantic_cube"]

# Clear existing data
papers_collection.delete_many({})
cube_collection.delete_many({})

# Aggregator: (year, month, category) -> list of paper dicts
aggregator = defaultdict(list)

with open(csv_file_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Extract date
        date_obj = datetime.datetime.strptime(row["update_date"], "%Y-%m-%d")
        year, month = date_obj.year, date_obj.month

        # Parse categories
        categories = row["cs_categories"].split()
        parent_categories = list({category_map.get(cat, "Other") for cat in categories})

        # Techniques from abstract
        techniques = extract_techniques(row["abstract"])

        # Build and insert individual paper
        paper_doc = {
            "id": row["id"],
            "title": row["title"],
            "abstract": row["abstract"],
            "categories": categories,
            "parent_categories": parent_categories,
            "techniques": techniques,
            "year": year,
            "month": month,
        }
        papers_collection.insert_one(paper_doc)

        # Aggregate by (year, month, category)
        for cat in categories:
            aggregator[(year, month, cat)].append(paper_doc)

# Naive abstract summary
def naive_aggregated_summary(papers):
    return " ".join(p["abstract"] for p in papers)


def llm_aggregated_summary(papers):
    abstracts_combined = "\n\n---\n\n".join([p["abstract"] for p in papers])
    # prompt = f"""Please provide a concise, expert-level summary that captures the main themes and key contributions 
    # from the following collection of research paper abstracts. Please identify the following:
    # - Main research themes
    # - Common methodologies
    # - Significant findings
    # - Emerging trends

    # From the following abstracts: {abstracts_combined}

    # Summary:"""

    prompt = f"""You are an expert computer science research assistant. Please provide a concise, expert-level summary that captures the main themes and key contributions 
    from the following collection of research paper abstracts. Please identify any main research themes, common methodologies, significant findings, and emerging trends from the following abstracts: {abstracts_combined}

    Summary:"""

    try:
        client = MetaAI()
        print('created MetaAI client')
        response = client.prompt(prompt)
        print(f"summary: {response['message']}")

        return response['message']
        
    except Exception as e:
        print(f"Error during summarization: {e}")
        return naive_aggregated_summary(papers)


# Insert aggregated cube documents
for (year, month, category), papers in aggregator.items():
    paper_ids = [p["id"] for p in papers]
    paper_titles = [p["title"] for p in papers]
    techniques = list({t for p in papers for t in p["techniques"]})
    parent_category = category_map.get(category, "Other")
    # summary = naive_aggregated_summary(papers)
    summary = llm_aggregated_summary(papers)

    cube_doc = {
        "year": year,
        "month": month,
        "category": category,
        "parent_category": parent_category,
        "paper_count": len(papers),
        "paper_ids": paper_ids,
        "paper_titles": paper_titles,
        "techniques": techniques,
        "aggregated_summary": summary,
    }

    try:
        cube_collection.insert_one(cube_doc)
    except pymongo.errors.OperationFailure as e:
        print(f"Insertion failed: {e}")
        sys.exit(1)


# import pymongo
# import sys
# import csv
# from collections import defaultdict
# import datetime
# from dotenv import load_dotenv
# import os

# load_dotenv()

# uri = os.getenv("MONGODB_URI")
# csv_file_path = "dataset/clean_fields_filter_date_sample50.csv"

# # connect to mongo
# try:
#     client = pymongo.MongoClient(uri)
#     print('client:   ', client)
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except pymongo.errors.ConfigurationError:
#     print(e)
#     sys.exit(1)


# db = client.paperDatabase
# print('db:', db)
# papers_collection = db["papers"]
# cube_collection = db["semantic_cube"]

# # Clear out old data
# cube_collection.delete_many({})
# papers_collection.delete_many({})

# # Dictionary to hold aggregated data
# # Key: (year, category) -> Value: list of rows (papers)
# aggregator = defaultdict(list)

# with open(csv_file_path, "r", encoding="utf-8") as f:
#     reader = csv.DictReader(f)
#     for row in reader:
#         # 1) Parse the update_date as a datetime
#         date_str = row["update_date"]  # e.g., "2022-10-17"
#         date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
#         year = date_obj.year
#         month = date_obj.month

#         # 2) Extract all cs categories (e.g., "cs.PL cs.CY" becomes a list)
#         categories = row["cs_categories"].split()

#         # 3.1) Group by (year, month, category) for each category the paper belongs to
#         for cat in categories:
#             aggregator[(year, month, cat)].append(row)

#         # 3.2) Build a document for the individual paper, storing all categories
#         paper_doc = {
#             "id": row["id"],
#             "title": row["title"],
#             "abstract": row["abstract"],
#             "categories": categories,  # store the complete list of categories
#             "year": year,
#             "month": month
#             # Add more fields if needed
#         }
#         papers_collection.insert_one(paper_doc)


# def naive_aggregated_summary(papers):
#     # Just concatenate abstracts
#     # Or you could pick the top 3 sentences from each abstract, etc.
#     all_abstracts = [p["abstract"] for p in papers]
#     return " ".join(all_abstracts)


# # Choose summary function
# summary_function = naive_aggregated_summary  # or llm_aggregated_summary


# # cube_collection.insert_one({"year":2000, "name":"Sabrina"})
# for (year, month, category), papers in aggregator.items():
#     # Compute aggregates
#     count = len(papers)
#     summary = summary_function(papers)
#     paper_ids = [p["id"] for p in papers]

#     # Build the document
#     doc = {
#         "year": year,
#         "month": month,
#         "category": category,
#         "paper_count": count,
#         "aggregated_summary": summary,
#         "paper_ids": paper_ids,
#         # Optional: store additional metadata, timestamps, etc.
#     }
#     try:
#         # Insert into MongoDB
#         cube_collection.insert_one(doc)
#     except pymongo.errors.OperationFailure:
#         sys.exit(1)
#     else:
#         pass
#         # print("doc inserted")

