
import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('FAANG_WATCH_API_KEY')
host = "faang-watch-api.p.rapidapi.com"

paths = ["/search", "/api/search", "/api/v1/search", "/jobs", "/api/jobs"]
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host,
    "Accept": "application/json"
}

for path in paths:
    url = f"https://{host}{path}"
    print(f"\nTesting {url}")
    try:
        res = requests.get(url, headers=headers, params={"text": "software"}, timeout=10)
        print(f"Status: {res.status_code}")
        print(f"Content-Type: {res.headers.get('Content-Type')}")
        if "application/json" in res.headers.get('Content-Type', ''):
            print(f"JSON Body: {res.text[:200]}")
        else:
            print(f"Non-JSON Body snippet: {res.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")
