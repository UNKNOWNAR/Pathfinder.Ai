
import requests
import os
from dotenv import load_dotenv

# Load from backend/.env
load_dotenv('backend/.env')

api_key = os.getenv('FAANG_WATCH_API_KEY')
url = "https://faang-watch.p.rapidapi.com/search"
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "faang-watch.p.rapidapi.com"
}

def test_query(params, label):
    print(f"\n--- Testing: {label} ---")
    print(f"Params: {params}")
    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"Status: {res.status_code}")
        data = res.json()
        if isinstance(data, list):
            print(f"Results count: {len(data)}")
            if len(data) > 0:
                print(f"First item keys: {list(data[0].keys())}")
                print(f"First item title: {data[0].get('title')}")
        elif isinstance(data, dict):
            # Check common keys for search results
            hits = data.get('hits', data.get('jobs', data.get('data', [])))
            print(f"Results count: {len(hits)}")
            print(f"Root keys: {list(data.keys())}")
            if len(hits) > 0:
                 print(f"First item title: {hits[0].get('title')}")
        else:
            print(f"Unexpected data type: {type(data)}")
            print(f"Raw: {str(data)[:200]}")
    except Exception as e:
        print(f"Error: {e}")

# Test 1: The parameters used in the harvester
test_query({
    "text": "software engineer",
    "location": "United States",
    "min_years_of_experience": 0,
    "seniority": "junior",
    "page_size": 10
}, "Harvester Defaults")

# Test 2: Relaxed parameters
test_query({
    "text": "software engineer",
    "page_size": 5
}, "Only Text Search")

# Test 3: Location only
test_query({
    "location": "India",
    "page_size": 5
}, "Only Location Search")
