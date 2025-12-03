"""
Company Research - MISSION, CULTURE, TECH STACK
"""
import google.generativeai as genai
from config.config import GEMINI_API_KEY
import json
import re

genai.configure(api_key=GEMINI_API_KEY)

def research_company(job: dict) -> dict:
    """Extract company mission, culture, tech stack."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        company_name = job.get('Company Name', 'Unknown')
        job_desc = job.get('Job Description', '')[:1500]
        
        if not job_desc:
            return {
                'Company Mission': 'N/A',
                'Company Values': 'N/A',
                'Company Culture Keywords': 'N/A',
                'Tech Stack Used': 'N/A'
            }
        
        print("   ⚙️ Extracting company info...")
        
        response = model.generate_content(f"""From this job posting for {company_name}, extract:
- Company mission (1 sentence, what they do)
- Company values (2-3 key words)
- Culture keywords (startup/remote/corporate/etc)
- Technologies used

Return as plain text, NOT JSON. Format:
Mission: ...
Values: ...
Culture: ...
Tech: ...

Job: {job_desc}""")
        
        response_text = response.text.strip()
        print(f"   Response: {response_text[:100]}...")
        
        # Parse response
        company_data = {
            'Company Mission': extract_field(response_text, 'Mission'),
            'Company Values': extract_field(response_text, 'Values'),
            'Company Culture Keywords': extract_field(response_text, 'Culture'),
            'Tech Stack Used': extract_field(response_text, 'Tech')
        }
        
        print(f"   ✅ Extracted company data\n")
        
        return company_data
        
    except Exception as e:
        print(f"   ❌ Company error: {e}")
        return {
            'Company Mission': 'N/A',
            'Company Values': 'N/A',
            'Company Culture Keywords': 'N/A',
            'Tech Stack Used': 'N/A'
        }

def extract_field(text: str, field_name: str) -> str:
    """Extract field value from response text."""
    try:
        # Find line starting with field name
        for line in text.split('\n'):
            if field_name.lower() in line.lower():
                value = line.split(':', 1)[1].strip()
                return value[:100] if value else 'N/A'
        return 'N/A'
    except:
        return 'N/A'
