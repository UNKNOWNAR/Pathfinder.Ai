
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('FAANG_WATCH_API_KEY')
host = "faang-watch.p.rapidapi.com"

# These endpoints gave 429 (exists) rather than 404 (doesn't exist)
endpoints = ["/jobs/search", "/v1/search", "/api/v1/jobs"]
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host,
    "Accept": "application/json"
}

print("Waiting 20 seconds to clear rate limits...")
time.sleep(20)

for ep in endpoints:
    url = f"https://{host}{ep}"
    print(f"\nTesting {url}")
    try:
        # Some APIs use 'q' instead of 'text'
        res = requests.get(url, headers=headers, params={"text": "software", "page_size": 1}, timeout=15)
        print(f"Status: {res.status_code}")
        print(f"Content-Type: {res.headers.get('Content-Type')}")
        if res.status_code == 200:
            print(f"Body snippet: {res.text[:200]}")
            try:
                data = res.json()
                print("Success! Parsed JSON.")
            except:
                print("Failed to parse JSON.")
        else:
            print(f"Body: {res.text}")
    except Exception as e:
        print(f"Error: {e}")
