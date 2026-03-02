
import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

api_key = os.getenv('JSEARCH_API_KEY') # Using JSearch key as discussed
url = "https://faang-watch.p.rapidapi.com/search"
headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "faang-watch.p.rapidapi.com"
}

params = {
    "text": "software engineer",
    "location": "United States",
    "min_years_of_experience": 0,
    "seniority": "junior",
    "page_size": 5
}

try:
    print(f"Testing FaangWatch API...")
    res = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text[:500]}...")

    # Try without specific filters to see if data exists
    print("\nTesting without seniority/experience filters...")
    res2 = requests.get(url, headers=headers, params={"text": "software engineer", "page_size": 5}, timeout=10)
    print(f"Status Code: {res2.status_code}")
    print(f"Response: {res2.text[:500]}...")

except Exception as e:
    print(f"Error: {e}")
