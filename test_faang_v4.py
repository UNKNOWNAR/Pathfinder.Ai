
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv('backend/.env')

api_key = os.getenv('FAANG_WATCH_API_KEY')
host = "faang-watch.p.rapidapi.com"
url = f"https://{host}/search"
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host
}

def test_request(params, label):
    print(f"\n--- Testing {label} ---")
    while True:
        try:
            res = requests.get(url, headers=headers, params=params, timeout=15)
            print(f"Status: {res.status_code}")

            if res.status_code == 429:
                print("Rate limited. Waiting 5 seconds...")
                time.sleep(5)
                continue

            if res.status_code == 200:
                data = res.json()
                print(f"Success! Type: {type(data)}")
                if isinstance(data, list):
                    print(f"Count: {len(data)}")
                    if data: print(f"Sample: {data[0].get('title')} at {data[0].get('company')}")
                elif isinstance(data, dict):
                    print(f"Keys: {list(data.keys())}")
                    # Check for nested results
                    for k in ['hits', 'jobs', 'data', 'results']:
                        if k in data:
                            print(f"Found '{k}' list of length {len(data[k])}")
                            if data[k]: print(f"Sample: {data[k][0].get('title')}")
            else:
                print(f"Error Body: {res.text}")
            break
        except Exception as e:
            print(f"Exception: {e}")
            break

# Try with just seniority as per some RapidAPI patterns
test_request({"seniority": "junior", "page_size": 1}, "Seniority only")

# Try with text and seniority
test_request({"text": "software", "seniority": "junior", "page_size": 1}, "Text and Seniority")

# Try capitalized
test_request({"text": "software", "seniority": "Junior", "page_size": 1}, "Text and Junior")
