import pymongo
import os
import sys
from meta_ai_api import MetaAI
import json

from query import run_pipeline

def get_user_input():
    query = input("Write your query: ")
    
    ai = MetaAI()

    ai.prompt(
        """Use this updated mapping as a reference for future queries. :
            # AI & ML
            "cs,LG": "AI",
            "cs,AI": "AI",
            "cs,CL": "AI",
            "cs,CV": "AI",
            "cs,NE": "AI",
            "cs,RO": "AI",

            # Security & Privacy
            "cs,CR": "Security",

            # Systems
            "cs,DC": "Systems",
            "cs,NI": "Systems",
            "cs,SE": "Systems",
            "cs,SY": "Systems",
            "cs,DS": "Systems",

            # Human Factors
            "cs,HC": "Human-Computer Interaction",
            "cs,CY": "Human-Computer Interaction",

            # Theory & Foundations
            "cs,IT": "Theory",
            "cs,NA": "Theory",
            "cs,ET": "Theory",

            # Signal & Vision
            "cs,SI": "Signal Processing",
            "cs,SD": "Signal Processing",

            # Hardware / Embedded
            "cs,CE": "Hardware",
            "cs,CC": "Hardware",

            # Digital Libraries
            "cs,DL": "Digital Libraries",
            """)
    
    # print(ai.prompt("List all mappings and abbreivations in the previous mapping provided. "))
    ai.prompt("For all subsequent queries, you are a expert at parsing natural language queries for "
                "database applications. Most prompts will be of the form:"
                "Find papers from <DATE-TOKEN> to <DATE-TOKEN> on <TOPIC-TOKEN>."
                "You will parse the appropriate data from <DATA-TOKEN> and <TOPIC-TOKEN> and feed it into a "
                "data pipeline def run_pipeline(category: cs,<TOPIC-TOKEN>, start_year: int, end_year: int, start_month: int, end_month: int)."
                "Each category should be formated as cs,<TOPIC-TOKEN> like cs,SI and cs,AI."
                "If a date is not specified, replace it with a 0."
                "Format your response as a list <category, start_year, end_year, start_month, end_month> without the opening and "
                "closing brackets.")
    
    parsed = ai.prompt(f"Use the previous instructions for to process this query: {query}")
    print(parsed)
    params = parsed['message'].split('\n')[0].split(", ")
    print(parsed['message'].split('\n'))
    # TODO: expand pipeline params to select on multiple categories
    pipeline_params = {
        'category': params[0].replace(",", "."),
        'start_year': int(params[1]),
        'end_year': int(params[2]),
        'start_month': int(params[3]),
        'end_month': int(params[4])
    }
    
    res = run_pipeline(*pipeline_params.values())
    print(res)
    with open("example_query.json", 'w') as file:
        json.dump(res[0], file, indent=4)


if __name__ == "__main__":
    print("Running")
    get_user_input()
