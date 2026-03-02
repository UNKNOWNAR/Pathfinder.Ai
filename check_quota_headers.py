
import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

api_key = os.getenv('FAANG_WATCH_API_KEY')
url = "https://faang-watch.p.rapidapi.com/search"
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "faang-watch.p.rapidapi.com"
}

try:
    res = requests.get(url, headers=headers, params={"text": "test"}, timeout=10)
    print(f"Status: {res.status_code}")
    for k, v in res.headers.items():
        if 'ratelimit' in k.lower():
            print(f"{k}: {v}")
except Exception as e:
    print(f"Error: {e}")
