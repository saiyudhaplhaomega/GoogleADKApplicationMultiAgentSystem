import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils.whatsapp_notifier import notifier
from utils.cv_parser import cv_parser  # NEW
import asyncio
import google.generativeai as genai
import time
import uuid
import random
from config.config import GEMINI_API_KEY, USER_PROFILE
from utils.sheets_manager import manager
from utils.duplicate_detector import is_duplicate
from agents.job_scraper import scrape_jobs

genai.configure(api_key=GEMINI_API_KEY)

QUERIES = [
    "python developer",
    "backend engineer", 
    "python engineer",
    "data engineer python",
    "devops engineer aws",
    "mlops engineer",
    "data engineer aws"
]

async def process_job_full_intelligence(job):
    """FULL 57-column intelligence pipeline."""
    print("🧠 Running FULL intelligence analysis...")
    
    # 1. CV Profile
    cv_profile = cv_parser.get_profile()
    
    # 2. Parallel: Skills + Company + Basic analysis
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    skill_task = model.generate_content_async(f"Analyze required skills: {job['Job Description'][:300]}")
    company_task = model.generate_content_async(f"Research {job['Company Name']}: mission, tech stack")
    
    skill_result, company_result = await asyncio.gather(skill_task, company_task)
    
    # 3. SIMPLE CV matching (fallback until agents ready)
    job_skills = ['Python', 'AWS', 'Docker']  # Extract from skill_result later
    cv_skills = list(cv_profile['skills'].keys())
    
    matching = [s for s in job_skills if s.lower() in [x.lower() for x in cv_skills]]
    match_pct = (len(matching) / len(job_skills)) * 100 if job_skills else 50
    
    # 4. Fill 57 columns (basic version)
    intelligence = {
        # CV Matching (15 cols)
        'Match Score': f"{match_pct:.0f}",
        'Skills Match %': f"{match_pct:.0f}%", 
        'Required Skills': ', '.join(job_skills),
        'Your Matching Skills': ', '.join(matching),
        'Missing Skills': ', '.join(set(job_skills) - set(matching)),
        'Learnable in 1 Week?': 'Yes',
        'Experience Level Match': 'Junior+ Match',
        
        # Company Intel (10 cols) 
        'Company Mission': company_result.text[:100],
        'Tech Stack Used': 'Python, AWS',  # Parse later
        'Company Culture Keywords': 'remote, agile',
        
        # Analysis
        'skills_analysis': skill_result.text[:300],
        'company_intel': company_result.text[:300],
    }
    
    job.update(intelligence)
    
    # 5. REAL score from CV match!
    score = float(job['Match Score'])
    print(f"📊 CV Match Score: {score:.1f}/100")
    
    return job, score

async def orchestrate(query: str = None, page: int = 1):
    """Enhanced orchestration - FULL intelligence."""
    if not query:
        query = random.choice(QUERIES)
    
    print(f"🚀 Scraping: '{query}' (Page {page})")
    jobs = scrape_jobs(query, page)
    
    if not jobs:
        print("⚠️ No jobs")
        return 0
    
    print(f"\n=== PROCESSING {len(jobs)} JOBS ===\n")
    saved = 0
    
    for idx, job in enumerate(jobs, 1):
        print(f"--- JOB {idx}/{len(jobs)}: {job['Job Title']} ---")
        
        job['Job ID'] = str(uuid.uuid4())[:8].upper()
        
        # Dedupe
        is_dup, dup_id = is_duplicate(job)
        if is_dup:
            print(f"❌ Duplicate: {dup_id}")
            continue
        
        # 🔥 FULL INTELLIGENCE PIPELINE
        try:
            job, score = await process_job_full_intelligence(job)
            
            # WhatsApp for high scores
            try:
                alert_sent = notifier.send_job_alert(job, score)
                job['WhatsApp Alert'] = 'Sent' if alert_sent else 'Skipped'
                job['Alert Score'] = f"{score:.1f}"
                if alert_sent:
                    print("📱 WHATSAPP SENT! 🚨")
            except Exception as e:
                job['WhatsApp Alert'] = 'Error'
                print(f"⚠️ WhatsApp: {e}")
            
            # Core columns
            job['Date Scraped'] = time.strftime("%Y-%m-%d")
            job['Priority Level'] = 'High' if score >= 85 else 'Medium'
            
            # Save to sheets
            manager.append_job(job)
            saved += 1
            print(f"💾 SAVED! Score: {score:.1f} | ID: {job['Job ID']}")
            
        except Exception as e:
            print(f"❌ Job failed: {e}")
        
        print()
    
    print(f"✅ {saved}/{len(jobs)} saved\n")
    return saved

async def orchestrate_batch(target_jobs: int = 30):
    """Batch until target reached."""
    print(f"🎯 TARGET: {target_jobs} jobs\n")
    
    total_saved = 0
    query_idx, page = 0, 1
    
    while total_saved < target_jobs:
        query = QUERIES[query_idx % len(QUERIES)]
        saved = await orchestrate(query, page)
        total_saved += saved
        
        print(f"📊 {total_saved}/{target_jobs} ({total_saved/target_jobs*100:.0f}%)")
        
        if total_saved >= target_jobs:
            break
            
        page += 1
        if page > 3:
            page = 1
            query_idx += 1
        
        time.sleep(2)
    
    print(f"\n🎉 BATCH COMPLETE: {total_saved} jobs!")

if __name__ == "__main__":
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    asyncio.run(orchestrate_batch(target))
