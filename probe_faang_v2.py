
import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('FAANG_WATCH_API_KEY')
host = "faang-watch-api.p.rapidapi.com"

# More exhaustive path testing for the confirmed host
paths = [
    "/",
    "/api/v1/jobs/search",
    "/v1/jobs",
    "/api/jobs/search",
    "/search/jobs",
    "/jobs-search"
]

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host,
    "Accept": "application/json"
}

print(f"Testing Host: {host}")
for path in paths:
    url = f"https://{host}{path}"
    try:
        # Some search APIs use 'q' or 'query' instead of 'text'
        params = {"text": "software", "page": 1}
        res = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Path: {path:20} | Status: {res.status_code} | Content-Type: {res.headers.get('Content-Type', 'N/A')}")
        if res.status_code == 200 and "json" in res.headers.get('Content-Type', ''):
            print(f"   SUCCESS! Body: {res.text[:100]}")
        elif res.status_code == 200:
             print(f"   HTML/Other snippet: {res.text[:50]}")
    except Exception as e:
        print(f"Path: {path:20} | Error: {e}")
