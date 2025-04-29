import pandas as pd
import os
from dotenv import load_dotenv
from time import sleep
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


CRITERIA = {
"comprehensiveness": '''How much detail does the answer provide to cover all the aspects and details of the
question? A comprehensive answer should be thorough and complete, without being redundant or irrelevant.
For example, if the question is ’What are the benefits and drawbacks of nuclear energy?’, a comprehensive
answer would provide both the positive and negative aspects of nuclear energy, such as its efficiency,
environmental impact, safety, cost, etc. A comprehensive answer should not leave out any important points
or provide irrelevant information. For example, an incomplete answer would only provide the benefits of
nuclear energy without describing the drawbacks, or a redundant answer would repeat the same information
multiple times. ''',
"diversity": '''How varied and rich is the answer in providing different perspectives and insights
on the question? A diverse answer should be multi-faceted and multi-dimensional, offering different
viewpoints and angles on the question. For example, if the question is ’What are the causes and effects
of climate change?’, a diverse answer would provide different causes and effects of climate change, such
as greenhouse gas emissions, deforestation, natural disasters, biodiversity loss, etc. A diverse answer
should also provide different sources and evidence to support the answer. For example, a single-source
answer would only cite one source or evidence, or a biased answer would only provide one perspective or
opinion.''',
"directness": '''How specifically and clearly does the answer address the question? A direct answer should
provide a clear and concise answer to the question. For example, if the question is ’What is the capital
of France?’, a direct answer would be ’Paris’. A direct answer should not provide any irrelevant or
unnecessary information that does not answer the question. For example, an indirect answer would be ’The
capital of France is located on the river Seine’.''',
"empowerment": '''How well does the answer help the reader understand and make informed judgements about
the topic without being misled or making fallacious assumptions. Evaluate each answer on the quality of
answer as it relates to clearly explaining and providing reasoning and sources behind the claims in the
answer.'''
}

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

df = pd.read_csv("response_pairs.csv")
results = []

def generate_prompt(query, response_a, response_b):
    return f""" You are an expert computer science research assistant.
    Given a question and two responses, Response A and Response B, assess which is better according to the following measures:

    1. Comprehensiveness: {CRITERIA['comprehensiveness']}
    2. Diversity: {CRITERIA['diversity']}
    3. Directness: {CRITERIA['directness']}
    4. Empowerment: {CRITERIA['empowerment']}

    Your assessment should include the following:
    - Winner: either Response A (if Response A is better), Response B (if Response B is better), or Tie (if both are fundamentally similar and the differences are immaterial).
    - Reasoning: a short explanation of why you chose the winner with respect to each of the criteria described above.

    ---QUESTION---
    {query}

    ---RESPONSE A---
    {response_a}

    ---RESPONSE B---
    {response_b}

    Please provide your answer in the following format:
    Winner: [Response A / Response B / Tie]
    Reason: [Your reasoning here]

    """

for i, row in df.iterrows():
    query = row['query']
    response_a = row['response_a']
    response_b = row['response_b']

    prompt = generate_prompt(query, response_a, response_b)

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant responsible for grading two answers to a question that are provided by two different people."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )

        content = response.choices[0].message.content.strip()
        if "Winner:" in content:
            winner_line, *reason_lines = content.split("Reason:")
            winner = winner_line.replace("Winner:", "").strip()
            reason = reason_lines[0].strip() if reason_lines else ""
        else:
            winner = "Unknown"
            reason = content

        results.append({
            "query": query,
            "response_a": response_a,
            "response_b": response_b,
            "winner": winner,
            "reason": reason
        })

    except Exception as e:
        print(f"⚠️ Error on row {i}: {e}")
        results.append({
            "query": query,
            "response_a": response_a,
            "response_b": response_b,
            "winner": "ERROR",
            "reason": str(e)
        })

    sleep(1.5) 

pd.DataFrame(results).to_csv("judged_comparisons.csv", index=False)
print("Judging complete. Results saved to judged_comparisons.csv")