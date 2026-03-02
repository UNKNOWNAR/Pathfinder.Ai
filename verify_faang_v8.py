
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('FAANG_WATCH_API_KEY')
host = "faang-watch.p.rapidapi.com"

# Testing the most promising endpoints based on previous 429 responses
endpoints = ["/active-jobs", "/jobs/search", "/active-jb-7d"]
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host,
    "Accept": "application/json"
}

print("Waiting 30 seconds to clear rate limits (Limit is very low: 30)...")
time.sleep(30)

for ep in endpoints:
    url = f"https://{host}{ep}"
    print(f"\nTesting {url}")
    try:
        res = requests.get(url, headers=headers, params={"text": "software", "page_size": 1}, timeout=15)
        print(f"Status: {res.status_code}")
        print(f"Content-Type: {res.headers.get('Content-Type')}")
        if res.status_code == 200:
            print(f"Body snippet: {res.text[:200]}")
            try:
                data = res.json()
                print("Success! Parsed JSON.")
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())}")
            except:
                print("Failed to parse JSON.")
        else:
            print(f"Body: {res.text}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(5) # Delay between attempts
