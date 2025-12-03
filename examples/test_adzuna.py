import requests
import os
from dotenv import load_dotenv

load_dotenv()

app_id = os.getenv("ADZUNA_APP_ID")
api_key = os.getenv("ADZUNA_API_KEY")

# Exact format from docs
url = f"https://api.adzuna.com/v1/api/jobs/de/search/1?app_id={app_id}&app_key={api_key}&what=python&results_per_page=10"

print(f"URL: {url[:100]}...")
print("\nTesting Adzuna...")

try:
    resp = requests.get(url, timeout=10, headers={"Accept": "application/json"})
    print(f"Status: {resp.status_code}")
    print(f"Headers: {resp.headers.get('content-type')}")
    
    data = resp.json()
    print(f"Response keys: {data.keys()}")
    print(f"Total jobs: {len(data.get('results', []))}")
    
    if data.get('results'):
        print("\nSample job:")
        job = data['results'][0]
        print(f"  Title: {job.get('title')}")
        print(f"  Company: {job.get('company', {}).get('display_name')}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
