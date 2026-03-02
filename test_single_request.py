
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv('backend/.env')

api_key = os.getenv('FAANG_WATCH_API_KEY')
host = "faang-watch.p.rapidapi.com"
url = f"https://{host}/search"

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": host
}

# Try the most basic query possible
params = {"text": "software"}

print(f"Testing URL: {url}")
print(f"Headers: {headers}")
print(f"Params: {params}")

try:
    response = requests.get(url, headers=headers, params=params)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
