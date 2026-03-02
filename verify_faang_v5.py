
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
    "X-RapidAPI-Host": host,
    "Accept": "application/json"
}

params = {
    "text": "software",
    "page_size": "5"
}

print("Waiting 10 seconds to clear rate limits...")
time.sleep(10)

print(f"Testing {url} with parameters {params}")
try:
    res = requests.get(url, headers=headers, params=params, timeout=15)
    print(f"Status: {res.status_code}")
    print(f"Content-Type: {res.headers.get('Content-Type')}")
    print(f"Body: {res.text[:500]}")

    if res.status_code == 200:
        try:
            data = res.json()
            print("Successfully parsed JSON!")
        except:
            print("Failed to parse JSON despite 200 OK.")
except Exception as e:
    print(f"Error: {e}")
