
import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

api_key = os.getenv('FAANG_WATCH_API_KEY')
host = "faang-watch.p.rapidapi.com"
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host
}

endpoints = ["/", "/search", "/jobs", "/api/search", "/api/v1/search"]

for ep in endpoints:
    url = f"https://{host}{ep}"
    print(f"\nTesting {url}...")
    try:
        # Using a very small page size and no complex filters to avoid 400s
        res = requests.get(url, headers=headers, params={"text": "software", "page_size": 1}, timeout=10)
        print(f"Status: {res.status_code}")
        print(f"Body: {res.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
