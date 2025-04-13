import pymongo
import os
import sys
from meta_ai_api import MetaAI
from query import run_pipeline


def main():
    ai = MetaAI()

    persistent_context = """Use the following mappings for all queries:

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
"cs.DL": "Digital Libraries"

You are an expert at parsing natural language queries for database applications.
For any given query, you must output exactly one line in CSV format containing six comma-separated values in this order:
    category,start_year,end_year,start_month,end_month
Do not include any additional text, explanations, or formatting; output only the CSV values.
- The category should be formatted as two items: the first token (e.g., "cs") and the topic (e.g., "AI") separated by a comma.
- If a query does not specify a full date range, assume the entire year (i.e. start_month = 1 and end_month = 12).
For example, if the query is "ai paper in 2024", you must output exactly:
    cs,AI,2024,2024,1,12
"""

    while True:
        query = input("Write your query (or type 'exit' to quit): ")
        if query.strip().lower() == "exit":
            break

        # Prepend the persistent context to the specific query prompt.
        full_prompt = (
            persistent_context
            + "\nNow, process the following query and output only the CSV line: "
            + query
        )

        parsed = ai.prompt(full_prompt)
        print("parsed:", parsed)

        try:
            # Parse the CSV output; expecting a result like:
            # cs,AI,2024,2024,1,12
            params_list = parsed["message"].strip().split(",")
            if len(params_list) != 6:
                raise ValueError(
                    "Unexpected format. Expected exactly 6 comma-separated values."
                )
            # Remove extra spaces if any.
            params_list = [token.strip() for token in params_list]
            pipeline_params = {
                "category": f"{params_list[0]}.{params_list[1]}",
                "start_year": int(params_list[2]),
                "end_year": int(params_list[3]),
                "start_month": int(params_list[4]),
                "end_month": int(params_list[5]),
            }
        except Exception as e:
            print("Error parsing response:", e)
            continue

        res = run_pipeline(*pipeline_params.values())
        if res:
            print("categories:", res.get("categories"))
            print("total_papers:", res.get("total_papers"))
            print("paper_ids:", res.get("paper_ids"))
            print("paper_titles:", res.get("paper_titles"))
            print("summaries:", res.get("summaries"))
        else:
            print("No results found.")


if __name__ == "__main__":
    print("Running")
    main()
