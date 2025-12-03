"""
Skill Analysis - BETTER PROMPTING + FALLBACK PARSING
"""
import google.generativeai as genai
import json
import re
from utils.cv_parser import cv_parser
from config.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def extract_skills_from_text(text: str) -> list:
    """Fallback: Extract skills using regex patterns."""
    skills = []
    
    # Common tech keywords
    tech_keywords = [
        'python', 'java', 'javascript', 'typescript', 'golang', 'rust', 'c++', 'c#', 'php', 'swift', 'kotlin',
        'react', 'vue', 'angular', 'nodejs', 'express', 'django', 'flask', 'fastapi', 'spring',
        'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'docker', 'kubernetes', 'jenkins', 'gitlab',
        'sql', 'postgres', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb', 'firestore',
        'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack',
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
        'data engineering', 'data pipeline', 'etl', 'apache spark', 'kafka', 'airflow',
        'devops', 'ci/cd', 'linux', 'windows', 'macos', 'unix',
        'rest api', 'graphql', 'websocket', 'grpc',
        'agile', 'scrum', 'kanban', 'waterfall',
        'text-to-speech', 'nlp', 'computer vision', 'image processing',
        'ios', 'android', 'mobile', 'app development', 'web development',
        'microservices', 'monolithic', 'serverless', 'lambda',
        'html', 'css', 'sass', 'webpack', 'babel', 'npm', 'yarn',
        'junit', 'pytest', 'mocha', 'jasmine', 'testing', 'tdd',
        'data science', 'analytics', 'tableau', 'power bi', 'looker',
        'architecture', 'design patterns', 'oop', 'functional programming'
    ]
    
    text_lower = text.lower()
    
    for keyword in tech_keywords:
        if keyword in text_lower:
            # Capitalize first letter of each word
            formatted = ' '.join(word.capitalize() for word in keyword.split())
            if formatted not in skills:
                skills.append(formatted)
    
    return skills

def parse_skills_text(text: str) -> list:
    """Parse skills from various formats: JSON, lists, comma-separated."""
    try:
        text = text.strip()
        
        # Remove markdown code blocks
        text = re.sub(r'``````', '', text).strip()
        text = text.strip('[]')
        
        # Try JSON parse
        try:
            skills = json.loads(text)
            if isinstance(skills, list):
                return [s.strip() for s in skills if s.strip()]
        except:
            pass
        
        # Split by comma or newline
        skills = re.split(r'[,\n]+', text)
        skills = [s.strip() for s in skills if s.strip() and len(s.strip()) > 2]
        
        return skills
    except Exception as e:
        print(f"   ⚠️ Parse error: {e}")
        return []

def format_for_sheets(skills: list) -> str:
    """Format skills as clean comma-separated text (NO JSON)."""
    if not skills:
        return "N/A"
    # Remove duplicates, limit to 15
    unique = list(dict.fromkeys(skills))[:15]
    result = ", ".join(unique)
    return result if result.strip() else "N/A"

def similarity(a: str, b: str) -> float:
    """Simple similarity score."""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()

def analyze_job_skills(job: dict) -> dict:
    """Extract job skills + compare with YOUR CV."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        job_desc = job.get('Job Description', '')[:3000]
        
        if not job_desc:
            print("   ⚠️ No job description")
            return {
                'Skills Match %': '0%',
                'Required Skills': 'N/A',
                'Your Matching Skills': 'N/A',
                'Missing Skills': 'N/A',
                'Learnable in 1 Week?': 'N/A',
                'Experience Level Match': 'N/A'
            }
        
        # STEP 1: Extract job skills with BETTER PROMPT
        print("   ⚙️ Extracting job skills...")
        
        prompt = f"""You are a technical recruiter. Extract ALL technical skills, tools, and technologies mentioned in this job posting.

Include:
- Programming languages (Python, Java, etc)
- Frameworks (React, Django, etc)
- Cloud platforms (AWS, Azure, GCP)
- Databases (SQL, MongoDB, etc)
- Tools & services (Docker, Kubernetes, Git, etc)
- Specializations (Data Engineering, DevOps, etc)

Return ONLY a comma-separated list, nothing else:
Python, AWS, Docker, Kubernetes, Data Engineering

Job Description:
{job_desc}"""
        
        response = model.generate_content(prompt)
        job_skills_raw = response.text.strip()
        print(f"   Raw response: {job_skills_raw[:100]}...")
        
        # Parse skills
        job_skills = parse_skills_text(job_skills_raw)
        
        # FALLBACK: If Gemini returns nothing, use regex fallback
        if not job_skills or job_skills == ['Unknown']:
            print("   ⚠️ Gemini returned nothing, using fallback extraction...")
            job_skills = extract_skills_from_text(job_desc)
        
        if not job_skills:
            job_skills = ['General Technical Skills']
        
        print(f"   ✅ Found {len(job_skills)} skills: {job_skills[:5]}...")
        
        # STEP 2: Get YOUR CV skills
        cv_profile = cv_parser.get_profile()
        cv_skills = list(cv_profile.get('skills', {}).keys())
        print(f"   📄 Your skills ({len(cv_skills)}): {cv_skills[:5]}...")
        
        # STEP 3: Match logic
        matching = []
        missing = []
        
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower().strip()
            found = False
            
            for cv_skill in cv_skills:
                cv_skill_lower = cv_skill.lower().strip()
                
                # Exact or partial match
                if (job_skill_lower == cv_skill_lower or
                    job_skill_lower in cv_skill_lower or
                    cv_skill_lower in job_skill_lower or
                    similarity(job_skill_lower, cv_skill_lower) > 0.75):
                    matching.append(job_skill)
                    found = True
                    break
            
            if not found:
                missing.append(job_skill)
        
        # STEP 4: Learnable skills
        learnable_keywords = ['react', 'javascript', 'typescript', 'kubernetes', 'spark', 'scala', 'docker', 'git', 'jenkins', 'kafka', 'jenkins', 'terraform']
        learnable = [s for s in missing if any(kw in s.lower() for kw in learnable_keywords)]
        
        # STEP 5: Calculate match percentage
        match_pct = (len(matching) / max(len(job_skills), 1)) * 100 if job_skills else 0
        
        print(f"   ✅ Match: {len(matching)}/{len(job_skills)} ({match_pct:.0f}%)")
        print(f"   ❌ Missing: {len(missing)}")
        print(f"   📚 Learnable: {len(learnable)}\n")
        
        # STEP 6: Format for Sheets (CLEAN TEXT ONLY)
        result = {
            'Skills Match %': f"{match_pct:.0f}%",
            'Required Skills': format_for_sheets(job_skills),
            'Your Matching Skills': format_for_sheets(matching) if matching else "N/A",
            'Missing Skills': format_for_sheets(missing) if missing else "N/A",
            'Learnable in 1 Week?': 'Yes' if learnable else 'No',
            'Experience Level Match': (
                'Advanced Match' if match_pct >= 80 else
                'Intermediate Match' if match_pct >= 50 else
                'Learning Opportunity'
            )
        }
        
        print(f"   📊 Final: {result['Skills Match %']} match\n")
        return result
        
    except Exception as e:
        print(f"   ❌ Skill error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'Skills Match %': '0%',
            'Required Skills': 'N/A',
            'Your Matching Skills': 'N/A',
            'Missing Skills': 'N/A',
            'Learnable in 1 Week?': 'N/A',
            'Experience Level Match': 'Error'
        }
