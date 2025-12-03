import requests
import json

url = "https://arbeitnow.com/api/job-board-api"

params = {
    "search": "python developer",
    "country": "de"
}

print("Testing Arbeitnow...")
try:
    resp = requests.get(url, params=params, timeout=10)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Total jobs: {len(data.get('data', []))}")
    
    if data.get('data'):
        print("\nSample job:")
        job = data['data'][0]
        print(f"  Title: {job.get('title')}")
        print(f"  Company: {job.get('company_name')}")
        print(f"  Location: {job.get('location')}")
        print(f"  Remote: {job.get('remote')}")
        print(f"  URL: {job.get('url')}")
    else:
        print("No jobs found.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
