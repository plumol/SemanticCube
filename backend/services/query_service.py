# services/query_service.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from query import run_pipeline
from utils.meta_ai import parse_query_to_params


def get_summary_from_natural_language(nl_query: str):
    """
    Convert natural language query to parameters using MetaAI,
    then run the semantic cube pipeline and return result.
    """
    params = parse_query_to_params(nl_query)
    result = run_pipeline(**params)
    if "rolled_up_summary" in result:
        return result["rolled_up_summary"]
    else:
        return "None"
