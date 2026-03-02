
import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('FAANG_WATCH_API_KEY')

# Testing potential host variations and POST method
hosts = [
    "faang-watch-api.p.rapidapi.com",
    "faang-watch.p.rapidapi.com",
    "faangwatch.p.rapidapi.com"
]

for host in hosts:
    print(f"\n=== Testing Host: {host} ===")
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": host,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Try GET /search
    try:
        url = f"https://{host}/search"
        res = requests.get(url, headers=headers, params={"text": "software"}, timeout=10)
        print(f"GET /search Status: {res.status_code}")
        if res.status_code == 200:
             print(f"GET Content-Type: {res.headers.get('Content-Type')}")
             print(f"GET snippet: {res.text[:100]}")
    except Exception as e:
        print(f"GET Error: {e}")

    # Try POST /search
    try:
        url = f"https://{host}/search"
        res = requests.post(url, headers=headers, json={"text": "software"}, timeout=10)
        print(f"POST /search Status: {res.status_code}")
        if res.status_code == 200:
             print(f"POST Content-Type: {res.headers.get('Content-Type')}")
             print(f"POST snippet: {res.text[:200]}")
    except Exception as e:
        print(f"POST Error: {e}")
