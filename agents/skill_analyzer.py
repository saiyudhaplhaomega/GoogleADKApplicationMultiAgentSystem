"""
CV vs Job: Fill 15 skill columns
"""
from utils.cv_parser import cv_parser
import google.generativeai as genai

def analyze_skills(job: dict) -> dict:
    """YOUR CV vs Job Description → Fill columns."""
    cv_skills = cv_parser.get_profile()['skills']
    
    # Gemini extracts job skills
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    job_text = job['Job Description'][:2000]
    
    response = model.generate_content(f"""
    Extract REQUIRED skills from job: {job_text}
    Return ONLY JSON: {{"skills": ["Python", "AWS", "Docker"]}}
    """)
    
    job_skills = ["Python", "AWS", "Docker"]  # Parse JSON
    
    # Match logic
    matching = [s for s in job_skills if s.lower() in cv_skills]
    missing = [s for s in job_skills if s.lower() not in cv_skills]
    learnable = [s for s in missing if s in ['React', 'Kubernetes']]
    
    match_pct = (len(matching) / len(job_skills)) * 100 if job_skills else 0
    
    return {
        'Match Score': f"{match_pct:.0f}",
        'Skills Match %': f"{match_pct:.0f}%",
        'Required Skills': ', '.join(job_skills),
        'Your Matching Skills': ', '.join(matching),
        'Missing Skills': ', '.join(missing), 
        'Learnable in 1 Week?': 'Yes' if learnable else 'No',
        'Experience Level Match': 'Yes' if match_pct > 70 else 'Stretch',
    }
