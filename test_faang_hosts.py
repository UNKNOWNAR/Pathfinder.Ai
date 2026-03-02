
import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

api_key = os.getenv('FAANG_WATCH_API_KEY')
hosts = ["faang-watch.p.rapidapi.com", "faangwatch.p.rapidapi.com", "faang-jobs.p.rapidapi.com"]

for host in hosts:
    url = f"https://{host}/search"
    print(f"\nTesting Host: {host}")
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": host
    }
    try:
        res = requests.get(url, headers=headers, params={"text": "software"}, timeout=10)
        print(f"Status: {res.status_code}")
        print(f"Body: {res.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
