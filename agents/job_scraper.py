import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import lxml  
import requests
from bs4 import BeautifulSoup
from config.config import JOB_PORTALS, USER_PROFILE
from dotenv import load_dotenv
import os
from typing import List, Dict, Any
import time
from urllib.parse import quote
from html.parser import HTMLParser
load_dotenv()
JSEARCH_KEY = os.getenv("JSEARCH_KEY")
ARBEITSAGENTUR_KEY = os.getenv("ARBEITSAGENTUR_KEY", "")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}



class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, d):
        self.text.append(d)
    
    def get_data(self):
        return ''.join(self.text).strip()

def strip_html(html_text: str) -> str:
    """Remove HTML tags from text."""
    if not html_text:
        return ''
    stripper = HTMLStripper()
    try:
        stripper.feed(html_text)
        return stripper.get_data()
    except:
        return html_text

def scrape_arbeitnow(query: str) -> List[Dict]:
    """Arbeitnow: Free European jobs API (Germany focused)."""
    try:
        url = "https://arbeitnow.com/api/job-board-api"
        params = {
            "search": query,
            "country": "de"
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        jobs = []
        for j in data.get('data', [])[:5]:
            # CLEAN HTML from description
            clean_desc = strip_html(j.get('description', ''))
            
            jobs.append({
                "Job Portal": "Arbeitnow",
                "Job Title": j.get('title', ''),
                "Company Name": j.get('company_name', ''),
                "Location": j.get('location', ''),
                "Remote Type": "Remote" if j.get('remote') else "On-site",
                "Job URL": j.get('url', ''),
                "Salary Range": "",
                "Job Description": clean_desc[:500],
                "Date Scraped": time.strftime("%Y-%m-%d")
            })
        return jobs
    except Exception as e:
        print(f"Arbeitnow error: {e}")
        return []



def scrape_arbeitsagentur(query: str, location="Berlin") -> List[Dict]:
    """Agentur für Arbeit: German public jobs API."""
    try:
        url = "https://jobsuche.api.arbeitsagentur.de/jobsuche/jobsuche-service"
        params = {
            "suchwoerter": query,
            "regionen": location,
            "page": 1
        }
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
        data = resp.json()
        jobs = []
        for match in data.get('matches', [])[:3]:
            jobs.append({
                "Job Portal": "Arbeitsagentur",
                "Job Title": match.get('jobtitle', ''),
                "Company Name": match.get('arbeitgebername', ''),
                "Location": match.get('arbeitgeberort', ''),
                "Remote Type": "",
                "Job URL": match.get('joburl', ''),
                "Job Description": match.get('kurzbeschreibung', '')[:500],
                "Date Scraped": time.strftime("%Y-%m-%d")
            })
        return jobs
    except Exception as e:
        print(f"Arbeitsagentur error: {e}")
        return []

def scrape_indeed_rss(query: str) -> List[Dict]:
    """Indeed RSS feed."""
    try:
        url = f"https://de.indeed.com/rss?q={quote(query)}&l=Berlin"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        #soup = BeautifulSoup(resp.content, 'xml')
        soup = BeautifulSoup(resp.content, 'html.parser')  # Changed
        jobs = []
        for item in soup.find_all('item')[:3]:
            try:
                title_text = item.find('title').text if item.find('title') else ''
                company_text = item.find('author').text if item.find('author') else ''
                jobs.append({
                    "Job Portal": "Indeed RSS",
                    "Job Title": title_text.split(' - ')[0] if ' - ' in title_text else title_text,
                    "Company Name": company_text,
                    "Location": "Berlin",
                    "Remote Type": "",
                    "Job URL": item.find('link').text if item.find('link') else '',
                    "Job Description": item.find('description').text[:500] if item.find('description') else '',
                    "Date Scraped": time.strftime("%Y-%m-%d")
                })
            except:
                continue
        return jobs
    except Exception as e:
        print(f"Indeed RSS error: {e}")
        return []

def scrape_linkedin_rss(query: str) -> List[Dict]:
    """LinkedIn RSS feed."""
    try:
        url = f"https://www.linkedin.com/jobs/search/?keywords={quote(query)}&location=Berlin&f_TPR=r2592000&rss=1"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.content, 'xml')
        jobs = []
        for item in soup.find_all('item')[:3]:
            try:
                title_text = item.find('title').text if item.find('title') else ''
                desc_text = item.find('description').text if item.find('description') else ''
                company = title_text.split(' at ')[-1] if ' at ' in title_text else ''
                jobs.append({
                    "Job Portal": "LinkedIn RSS",
                    "Job Title": title_text.split(' at ')[0] if ' at ' in title_text else title_text,
                    "Company Name": company,
                    "Location": "Berlin",
                    "Remote Type": "",
                    "Job URL": item.find('link').text if item.find('link') else '',
                    "Job Description": desc_text[:500],
                    "Date Scraped": time.strftime("%Y-%m-%d")
                })
            except:
                continue
        return jobs
    except Exception as e:
        print(f"LinkedIn RSS error: {e}")
        return []

def scrape_xing_rss(query: str) -> List[Dict]:
    """Xing RSS feed (if available)."""
    try:
        # Xing RSS: https://www.xing.com/jobs/rss (limited, may require auth)
        url = f"https://www.xing.com/jobs/rss?search={quote(query)}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 403:
            return []
        soup = BeautifulSoup(resp.content, 'xml')
        jobs = []
        for item in soup.find_all('item')[:3]:
            try:
                jobs.append({
                    "Job Portal": "Xing",
                    "Job Title": item.find('title').text if item.find('title') else '',
                    "Company Name": "",
                    "Location": "Berlin",
                    "Remote Type": "",
                    "Job URL": item.find('link').text if item.find('link') else '',
                    "Job Description": item.find('description').text[:500] if item.find('description') else '',
                    "Date Scraped": time.strftime("%Y-%m-%d")
                })
            except:
                continue
        return jobs
    except Exception as e:
        print(f"Xing RSS error: {e}")
        return []

def scrape_adzuna(query: str, page: int = 1) -> List[Dict]:
    """Adzuna: Free German jobs API with pagination."""
    try:
        app_id = os.getenv("ADZUNA_APP_ID")
        api_key = os.getenv("ADZUNA_API_KEY")
        
        if not app_id or not api_key:
            print("⚠️  Adzuna keys missing")
            return []
        
        url = f"https://api.adzuna.com/v1/api/jobs/de/search/{page}?app_id={app_id}&app_key={api_key}&what={quote(query)}&results_per_page=10"
        
        resp = requests.get(url, timeout=10, headers={"Accept": "application/json"})
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        jobs = []
        for j in data.get('results', [])[:10]:
            jobs.append({
                "Job Portal": "Adzuna",
                "Job Title": j.get('title', ''),
                "Company Name": j.get('company', {}).get('display_name', ''),
                "Location": j.get('location', {}).get('display_name', ''),
                "Remote Type": "On-site",
                "Job URL": j.get('redirect_url', ''),
                "Salary Range": f"{j.get('salary_min', '')}-{j.get('salary_max', '')}" if j.get('salary_min') else "",
                "Job Description": strip_html(j.get('description', ''))[:500],
                "Date Scraped": time.strftime("%Y-%m-%d")
            })
        return jobs
    except Exception as e:
        print(f"Adzuna error: {e}")
        return []

def scrape_jobs(query: str = "python developer", page: int = 1) -> List[Dict]:
    """Multi-platform: Adzuna (paginated) + RSS."""
    all_jobs = []
    
    print(f"Scraping Adzuna (query: '{query}', page: {page})...")
    all_jobs += scrape_adzuna(query, page)
    time.sleep(1)
    
    print("Scraping Indeed RSS...")
    all_jobs += scrape_indeed_rss(query)
    
    return all_jobs



if __name__ == "__main__":
    jobs = scrape_jobs("senior python developer")
    print(f"\nTotal scraped: {len(jobs)} jobs")
    for j in jobs[:5]:
        print(f"  - {j['Job Title']} at {j['Company Name']} ({j['Job Portal']})")
