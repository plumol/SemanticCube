import pymongo
import sys
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGODB_URI")

try:
    client = pymongo.MongoClient(uri)
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except pymongo.errors.ConfigurationError:
    print("Invalid URI or connection error.")
    sys.exit(1)

db = client.paperDatabase
cube_collection = db["semantic_cube"]

def parse_date(date_str):
    if not date_str:
        return None, None
    try:
        year, month = date_str.split("-")
        return int(year), int(month)
    except ValueError:
        print("Invalid date format. Use YYYY-MM.")
        return None, None

def run_pipeline(match_stage):
    pipeline = []
    if match_stage:
        pipeline.append({"$match": match_stage})

    pipeline.append({
        "$group": {
            "_id": None,
            "titles": {"$push": "$title"},
            "total_papers": {"$sum": "$paper_count"},
            "techniques": {"$addToSet": "$techniques"},
            "categories": {"$addToSet": "$category"},
            "summaries": {"$push": "$aggregated_summary"},
        }
    })

    return list(cube_collection.aggregate(pipeline))


# === User Interaction ===
while True:
    print("\nSelect OLAP Operation to Perform:")
    print("1. Roll-up (Generalization)")
    print("2. Drill-down (Detail Exploration)")
    print("3. Slice/Dice (Filtering)")
    print("4. Pivot (Compare focus over time)")
    print("q. Quit")
    op = input("Choose an operation: ").strip()

    if op.lower() == 'q':
        break

    match_stage = {}

    if op == '1':  # Roll-up
        parent_category = input("Enter parent category (e.g., AI, Systems): ").strip()
        start_date = input("Start date (YYYY-MM): ").strip()
        end_date = input("End date (YYYY-MM): ").strip()

        start_year, start_month = parse_date(start_date)
        end_year, end_month = parse_date(end_date)

        match_stage["parent_category"] = parent_category
        if start_year or end_year:
            match_stage["year"] = {}
            if start_year: match_stage["year"]["$gte"] = start_year
            if end_year: match_stage["year"]["$lte"] = end_year
        if start_month or end_month:
            match_stage["month"] = {}
            if start_month: match_stage["month"]["$gte"] = start_month
            if end_month: match_stage["month"]["$lte"] = end_month

    elif op == '2':  # Drill-down
        technique = input("Enter technique (e.g., BERT): ").strip()
        category = input("Enter category (e.g., cs.CL): ").strip()
        match_stage["techniques"] = technique
        match_stage["category"] = category

    elif op == '3':  # Slice/Dice
        technique = input("Enter technique (e.g., Transformer): ").strip()
        category = input("Enter category (e.g., cs.CV or cs.CL): ").strip()
        match_stage["techniques"] = technique
        match_stage["category"] = category

    elif op == '4':  # Pivot
        print("\nPivot analysis requires comparison over time.")
        print("We recommend running multiple roll-up queries (e.g., NLP vs CV vs Robotics)")
        print("and comparing trends year by year.")
        continue

    else:
        print("Invalid option. Choose 1–4 or q.")
        continue

    result = run_pipeline(match_stage)
    if result:
        r = result[0]
        print("\nTotal Papers:", r.get("total_papers", 0))
        print("Categories:", r.get("categories", []))
        print("Techniques:", r.get("techniques", []))
        print("Paper Titles:")
        for title in r.get("titles", []):
            print("-", title)
        print("\nSummaries:")
        for summary in r.get("summaries", []):
            print("-", summary[:300], "...\n")
    else:
        print("No results found.")



# import pymongo
# import sys
# from dotenv import load_dotenv
# import os

# load_dotenv()

# uri = os.getenv("MONGODB_URI")

# try:
#     client = pymongo.MongoClient(uri)
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
    
# except pymongo.errors.ConfigurationError:
#     print(e)
#     print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
#     sys.exit(1)

# db = client.paperDatabase
# cube_collection = db["semantic_cube"]

# '''
# # Example: Find all 2022 papers in "cs.PL"
# result = cube_collection.find_one({"year": 2022, "category": "cs.PL"})
# # result = cube_collection.find_one({"year": 2025, "category": "cs.CV"})
# if result:
#     print("Paper Count:", result["paper_count"])
#     print("Summary:", result["aggregated_summary"])
# else:
#     print("No data found for (2022, cs.PL)")
# '''

# def run_pipeline(category=None, start_year=None, end_year=None, start_month=None, end_month=None):
#     # Build the $match stage dynamically based on provided parameters.
#     match_stage = {}
#     if category:
#         match_stage["category"] = category

#     # Build the year filter if provided
#     if start_year or end_year:
#         year_filter = {}
#         if start_year:
#             try:
#                 year_filter["$gte"] = int(start_year)
#             except ValueError:
#                 print("Invalid start year. It should be a number.")
#                 return []
#         if end_year:
#             try:
#                 year_filter["$lte"] = int(end_year)
#             except ValueError:
#                 print("Invalid end year. It should be a number.")
#                 return []
#         if year_filter:
#             match_stage["year"] = year_filter

#     # Build the month filter if provided
#     if start_month or end_month:
#         month_filter = {}
#         if start_month:
#             try:
#                 month_filter["$gte"] = int(start_month)
#             except ValueError:
#                 print("Invalid start month. It should be a number.")
#                 return []
#         if end_month:
#             try:
#                 month_filter["$lte"] = int(end_month)
#             except ValueError:
#                 print("Invalid end month. It should be a number.")
#                 return []
#         if month_filter:
#             match_stage["month"] = month_filter

#     pipeline = []
#     if match_stage:
#         pipeline.append({"$match": match_stage})
    
#     # Grouping stage: adjust _id if needed
#     pipeline.append({
#         "$group": {
#             "_id": None,
#             "categories": {"$push": "$category"},
#             "total_papers": {"$sum": "$paper_count"},
#             "paper_ids": {"$push": "paper_ids"},
#             "summaries": {"$push": "$aggregated_summary"}
#         }
#     })
    
#     # print("pipeline: ", pipeline)
#     return list(cube_collection.aggregate(pipeline))

# '''
# category_pipeline = [
#     {"$match": {"category": "cs.CV"}},
#     {
#         "$group": {
#             "_id": None,
#             "total_papers": {"$sum": "$paper_count"},
#             "summaries": {"$push": "$aggregated_summary"}
#         }
#     }
# ]
# rollup_result = list(cube_collection.aggregate(category_pipeline))
# if rollup_result:
#     total_papers = rollup_result[0]["total_papers"]
#     all_summaries = rollup_result[0]["summaries"]
#     print(total_papers)
#     print(all_summaries)
# '''

# while True:
#     category = input("Enter category (e.g., cs.CV) or 'q' to quit: ")
#     if category.lower() == 'q':
#         break

#     start_date = input("Enter start date (YYYY-MM) or press Enter to skip, 'q' to quit: ")
#     if start_date.lower() == 'q':
#         break

#     end_date = input("Enter end date (YYYY-MM) or press Enter to skip, 'q' to quit: ")
#     if end_date.lower() == 'q':
#         break

#     # Parse start date into year and month if provided
#     if start_date:
#         try:
#             start_year, start_month = start_date.split("-")
#         except ValueError:
#             print("Invalid start date format. Please use YYYY-MM")
#             continue
#     else:
#         start_year, start_month = None, None

#     # Parse end date into year and month if provided
#     if end_date:
#         try:
#             end_year, end_month = end_date.split("-")
#         except ValueError:
#             print("Invalid end date format. Please use YYYY-MM")
#             continue
#     else:
#         end_year, end_month = None, None

#     # Run the pipeline with the user-specified parameters.
#     result = run_pipeline(
#         category,
#         start_year if start_year else None,
#         end_year if end_year else None,
#         start_month if start_month else None,
#         end_month if end_month else None
#     )

#     if result:
#         categories = result[0].get("categories", [])
#         total_papers = result[0].get("total_papers", 0)
#         all_summaries = result[0].get("summaries", [])
#         print("Categories:", categories)
#         print("Total Papers:", total_papers)
#         print("Summaries:", all_summaries, '\n\n')
#     else:
#         print("No results found.")

