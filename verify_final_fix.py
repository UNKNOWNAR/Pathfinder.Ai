
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv('backend/.env')

api_key = os.getenv('FAANG_WATCH_API_KEY')
host = "faang-watch-api.p.rapidapi.com"
url = f"https://{host}/search"
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host
}

params = {
    "text": "software engineer",
    "location": "United States",
    "min_years_of_experience": 0,
    "seniority": "Junior",
    "page_size": 5
}

print(f"Testing new host: {host}")
try:
    res = requests.get(url, headers=headers, params=params, timeout=15)
    print(f"Status: {res.status_code}")
    print(f"Raw Body: {res.text[:500]}")
    if res.status_code == 200:
        try:
            data = res.json()
            hits = data.get('hits', [])
            print(f"Success! Found {len(hits)} jobs.")
            if hits:
                print(f"Sample Job: {hits[0].get('title')} at {hits[0].get('company')}")
        except Exception as json_e:
            print(f"JSON Parse Error: {json_e}")
    else:
        print(f"Body: {res.text}")
except Exception as e:
    print(f"Error: {e}")
