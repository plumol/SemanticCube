# backend/test_filter.py
import requests
import json

def test_filter_endpoint(query: str):
    url = "http://localhost:8000/filter"
    payload = {
        "query": query,
        "mode": "filtering"
    }
    
    print(f"\nTesting query: '{query}'")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"Total papers found: {data['total_count']}")
            print("\nPapers:")
            for i, paper in enumerate(data['papers'], 1):
                print(f"\n{i}. Title: {paper['title']}")
                print(f"   Category: {paper['category']}")
                print(f"   Date: {paper['year']}/{paper['month']}")
                print(f"   Summary: {paper['summary'][:200]}...")
        else:
            print(f"Error: {response.json()['detail']}")
    except Exception as e:
        print(f"Error making request: {e}")

# Test cases
test_queries = [
    "Show me AI papers from March 2024",
    "Machine learning papers from January to March 2024",
    "Recent computer vision research",
    "NLP papers from last year",
    "Robotics papers in 2024",
    "Security papers from February 2024",
]

if __name__ == "__main__":
    print("Testing Filter Endpoint")
    print("=" * 50)
    
    for query in test_queries:
        test_filter_endpoint(query)
        print("\n" + "=" * 50)