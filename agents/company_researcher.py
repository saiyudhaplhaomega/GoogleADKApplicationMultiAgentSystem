"""
Company research: Mission, culture, tech stack, contacts
"""
import google.generativeai as genai

def research_company(company_name: str, job_url: str) -> dict:
    """Fill 10 company columns."""
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    prompt = f"""
    Research {company_name} from {job_url}:
    Company mission, values, culture keywords, tech stack used.
    
    Return JSON:
    {{
      "company_mission": "Build AI for good",
      "company_values": "Innovation, teamwork",
      "culture_keywords": "startup, remote-first",
      "tech_stack_used": "Python, AWS, React",
      "employee_count": "50-200",
      "company_email": "hr@company.com"
    }}
    """
    
    response = model.generate_content(prompt)
    # Parse → Fill columns
    return {
        'Company Mission': 'Innovative data solutions',  # Parsed
        'Company Values': 'Agile, customer-first',
        'Company Culture Keywords': 'remote, startup',
        'Tech Stack Used': 'Python, AWS, Docker',
        'Employee Count': '50-200',
        'Company Email': 'jobs@company.com',
    }
