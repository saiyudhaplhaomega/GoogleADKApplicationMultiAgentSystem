import http.client
import json

conn = http.client.HTTPSConnection("jsearch.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "048b6f4b56msh4d7ca8caf4cc9fbp1e1106jsn2bbab5cce13e",
    'x-rapidapi-host': "jsearch.p.rapidapi.com"
}

# Advanced query with filters
conn.request("GET", "/search?query=python%20developer%20jobs%20in%20germany&page=1&num_pages=1&country=de&language=German&date_posted=today&employment_types=FULLTIME,CONTRACTOR,PARTTIME&radius=300", headers=headers)

res = conn.getresponse()
data = res.read()

response = json.loads(data.decode("utf-8"))
print("Status:", res.status)
print("Total jobs:", len(response.get('data', [])))
if response.get('data'):
    print("\nSample job:")
    job = response['data'][0]
    print(f"  Title: {job.get('job_title')}")
    print(f"  Company: {job.get('employer_name')}")
    print(f"  Location: {job.get('job_location')}")
    print(f"  Posted: {job.get('job_posted_at')}")
    print(f"  URL: {job.get('job_apply_link')}")
else:
    print("No jobs found with filters.")
