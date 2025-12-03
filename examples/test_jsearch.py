import requests
import os
from dotenv import load_dotenv

load_dotenv()
JSEARCH_KEY = os.getenv("JSEARCH_KEY")

print(f"Key: {JSEARCH_KEY[:20]}...")

url = "https://jsearch.p.rapidapi.com/search"
headers = {
    "X-RapidAPI-Key": JSEARCH_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}
params = {
    "query": "python developer germany",
    "location": "Germany",
    "page": 1,
    "num_pages": 1
}

print("Testing JSearch...")
try:
    resp = requests.get(url, headers=headers, params=params, timeout=60)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
except Exception as e:
    print(f"Error: {e}")
