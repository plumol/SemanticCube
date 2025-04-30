# utils/meta_ai.py
from meta_ai_api import MetaAI


def parse_query_to_params(query: str) -> dict:
    persistent_context = """You are an expert at parsing natural language queries about computer science research papers. Your task is to convert natural language queries into structured database parameters.

        # Category Mappings (use these exact mappings):
        AI & ML:
        - "cs.LG" for Machine Learning
        - "cs.AI" for Artificial Intelligence
        - "cs.CL" for Computational Linguistics & NLP
        - "cs.CV" for Computer Vision
        - "cs.NE" for Neural/Evolutionary Computing
        - "cs.RO" for Robotics

        Security & Privacy:
        - "cs.CR" for Cryptography & Security

        Systems:
        - "cs.DC" for Distributed Computing
        - "cs.NI" for Networking & Internet Architecture
        - "cs.SE" for Software Engineering
        - "cs.SY" for Systems & Control
        - "cs.DS" for Data Structures & Algorithms

        Human Factors:
        - "cs.HC" for Human-Computer Interaction
        - "cs.CY" for Computers & Society

        Theory & Foundations:
        - "cs.IT" for Information Theory
        - "cs.NA" for Numerical Analysis
        - "cs.ET" for Emerging Technologies

        Signal & Vision:
        - "cs.SI" for Social & Information Networks
        - "cs.SD" for Sound

        Hardware:
        - "cs.CE" for Computer Engineering
        - "cs.CC" for Computational Complexity

        Digital Libraries:
        - "cs.DL" for Digital Libraries

        Rules for parsing:
        1. For date ranges:
        - If only a year is mentioned (e.g., "2024"), use months 1-12
        - If a specific month is mentioned (e.g., "March 2024"), use that exact month
        - For relative terms:
            - "recent" = last 3 months
            - "this year" = current year, months 1-12
            - "last year" = previous year, months 1-12
        2. For categories:
        - Match to the closest category from the mapping
        - If multiple categories could apply, choose the most specific one
        - If no category is specified, use "cs.AI" as default

        Output format: Exactly one line in CSV format with six values:
        domain,category,start_year,start_month,end_year,end_month

        Examples:
        Query: "recent papers about machine learning"
        Output: cs,LG,2024,1,2024,3

        Query: "computer vision research from 2023"
        Output: cs,CV,2023,1,2023,12

        Query: "nlp papers from March to June 2024"
        Output: cs,CL,2024,3,2024,6
        """

    ai = MetaAI()
    full_prompt = (
        persistent_context
        + "\nNow, process the following query and output only the CSV line: "
        + query
    )
    parsed = ai.prompt(full_prompt)
    csv_line = parsed["message"].strip()

    tokens = [t.strip() for t in csv_line.split(",")]
    if len(tokens) != 6:
        raise ValueError(f"Expected 6 comma-separated tokens but got: {tokens}")

    return {
        "category": f"{tokens[0]}.{tokens[1]}",
        "start_year": int(tokens[2]),
        "start_month": int(tokens[3]),
        "end_year": int(tokens[4]),
        "end_month": int(tokens[5]),
    }
