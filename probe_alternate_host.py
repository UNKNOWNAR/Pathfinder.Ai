
import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('FAANG_WATCH_API_KEY')
host = "faang-watch.p.rapidapi.com"

# Common job API paths on RapidAPI
paths = ["/search", "/active-jobs", "/jobs/search", "/v1/search", "/api/v1/jobs"]
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host
}

print(f"Testing Host: {host}")
for path in paths:
    url = f"https://{host}{path}"
    try:
        res = requests.get(url, headers=headers, params={"text": "software"}, timeout=10)
        print(f"Path: {path:15} | Status: {res.status_code} | Content-Type: {res.headers.get('Content-Type', 'N/A')}")
        if res.status_code == 200:
            print(f"   Body: {res.text[:100]}")
    except Exception as e:
        print(f"Path: {path:15} | Error: {e}")
