import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "credentials.json")

JOB_PORTALS = ["indeed", "linkedin", "xing", "stepstone"]  

USER_PROFILE = {
    "skills": ["Python", "Django", "PostgreSQL", "Docker"],
    "job_titles": [
        "Python Developer",
        "Python Engineer",
        "Backend Engineer",
        "Software Engineer",
        "Python Entwickler",
        "Softwareentwickler Python"
    ],
    "experience_level": "Senior",
    "location_pref": [
        "remote",
        "Berlin, Germany",
        "Munich, Germany",
        "Hamburg, Germany",
        "Frankfurt, Germany",
        "Stuttgart, Germany",
        "Cologne, Germany",
        "Düsseldorf, Germany",
        "Leipzig, Germany",
        "Remote Germany"
    ],
    "remote_pref": "Remote/Hybrid"
}

SHEETS_ID = os.getenv("SHEETS_ID")

COLUMNS = [
    "Job ID", "Date Posted", "Date Scraped", "Job Portal", "Job URL", "Priority Level", "Verification Status",
    "Job Title", "Company Name", "Location", "Remote Type", "Salary Range", "Benefits", "Application Deadline",
    "Match Score", "Skills Match %", "Required Skills", "Your Matching Skills", "Missing Skills", "Learnable in 1 Week?",
    "Experience Level Match", "Company Mission", "Company Values", "Company Culture Keywords", "Tech Stack Used",
    "Recent Projects", "Employee Count", "Company Email", "HR Contact Name", "HR Contact Title", "HR LinkedIn URL",
    "Recruiter Email", "Best Contact Method", "Auto-Apply Approved", "Applied", "Application Date",
    "Application Actually Sent", "Email Confirmation Received", "Application Method", "CV Version Used",
    "Cover Letter Used", "Follow-up Email Sent", "Follow-up Date", "Response Received", "Response Date",
    "Response Type", "Days to Response", "Interview Scheduled", "Interview Date", "Final Status",
    "Rejection Reason", "Portal Performance Tag", "Notes", "Tags", "Red Flags", "Green Flags", "Job Description"
]

assert len(COLUMNS) == 57
