
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

def test(params, label):
    print(f"\n--- {label} ---")
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status: {res.status_code}")
        print(f"Body: {res.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")

# Try with minimal params
test({"text": "engineer"}, "Minimal Search")

# Try with capitalized seniority as per docs "Junior"
test({"text": "engineer", "seniority": "Junior"}, "Capitalized Seniority")

# Try without the /search path just in case
print("\n--- Testing base path ---")
try:
    res = requests.get("https://faang-watch.p.rapidapi.com/", headers=headers, timeout=10)
    print(f"Base Path Status: {res.status_code}")
    print(f"Base Path Body: {res.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
