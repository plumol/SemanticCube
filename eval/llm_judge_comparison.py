import pandas as pd
import os
from dotenv import load_dotenv
from time import sleep
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from typing import Dict 
import re


load_dotenv()
llm = ChatOpenAI(model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"))

CRITERIA = {
    "comprehensiveness": "How much detail does the answer provide to cover all aspects and details of the question?",
    "diversity": "How varied and rich is the answer in providing different perspectives and insights on the question?",
    "directness": "How specifically and clearly does the answer address the question?",
    "empowerment": "How well does the answer help the reader understand and make informed judgements without being misled or making fallacious assumptions?"
}

def sanitize_input(text: str) -> str:
    """Sanitize input to escape any special characters or quotes."""
    # Replace newline characters with a space
    text = text.replace('\n', ' ').replace('\r', '')
    # Replace single quotes with escaped single quotes
    text = re.sub(r"'", "\\'", text)
    # Replace double quotes with escaped double quotes
    text = re.sub(r'"', '\\"', text)
    # Replace backslashes with escaped backslashes
    text = re.sub(r'\\', '\\\\', text)
    return text

def build_judge_prompt(query: str, response_a, response_b, response_c) -> str:
    criteria_block = "\n".join([f"• **{k.capitalize()}**: {v}" for k, v in CRITERIA.items()])
    response_a = sanitize_input(response_a)
    response_b = sanitize_input(response_b)
    response_c = sanitize_input(response_c)

    prompt = f"""You are an expert evaluator for research QA systems.

Your task is to assess and score three answers to the same query using the following criteria:

{criteria_block}

---  
Query: {query}

Answers:
1. **NAIVE**: {response_a}
2. **GRAPHRAG**: {response_b}
3. **CUBE**: {response_c}

You will evaluate each answer based on the criteria above.

For each criterion, assign a score from 1 (poor) to 5 (excellent) for each method (NAIVE, GRAPHRAG, CUBE). Respond in the following JSON format:

{{
  "naive": {{ "comprehensiveness": x, "diversity": y, "directness": z, "empowerment": w }},
  "graphrag": {{ "comprehensiveness": x, "diversity": y, "directness": z, "empowerment": w }},
  "cube": {{ "comprehensiveness": x, "diversity": y, "directness": z, "empowerment": w }}
}}

Only return the JSON.
"""
    return prompt

def evaluate_responses(df: pd.DataFrame) -> pd.DataFrame:
    results = []
    for _, row in df.iterrows():
        prompt = build_judge_prompt(row["query"], row['naive_response'], row['graphrag_response'], row['semantic_cube_response'])
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            scores = eval(response.content)
            result_row = {
                "query": row["query"],
                **{f"naive_{k}": v for k, v in scores["naive"].items()},
                **{f"graphrag_{k}": v for k, v in scores["graphrag"].items()},
                **{f"cube_{k}": v for k, v in scores["cube"].items()}
            }
            results.append(result_row)
        except Exception as e:
            print(f"Error on query '{row['query']}': {e}")
            continue

    return pd.DataFrame(results)
