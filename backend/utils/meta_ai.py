# utils/meta_ai.py
from meta_ai_api import MetaAI


def parse_query_to_params(query: str) -> dict:
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
    category,start_year,start_month,end_year,end_month
Do not include any additional text, explanations, or formatting; output only the CSV values.
- The category should be formatted as two items: the first token (e.g., "cs") and the topic (e.g., "AI") separated by a comma.
- If a query does not specify a full date range, assume the entire year (i.e. start_month = 1 and end_month = 12).
For example, if the query is "ai paper in 2024", you must output exactly:
    cs,AI,2024,1,2024,12
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
