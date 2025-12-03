import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from utils.whatsapp_notifier import notifier
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
    "full stack python",
    "senior python",
    "django developer",
    "data engineer python"
]

async def process_job_parallel(job):
    """Parallel: Analyze skills + Research company (async)."""
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    skill_task = model.generate_content_async(
        f"Analyze required skills for: {job['Job Description'][:300]}"
    )
    company_task = model.generate_content_async(
        f"Research company {job['Company Name']}: mission, culture, tech stack"
    )
    
    skill_result, company_result = await asyncio.gather(skill_task, company_task)
    
    return {
        "skills_analysis": skill_result.text[:300],
        "company_intel": company_result.text[:300]
    }

async def orchestrate(query: str = None, page: int = 1):
    """Process single query/page - WHATSAPP ALERTS ADDED."""
    if not query:
        query = random.choice(QUERIES)
    
    print(f"🚀 Scraping (Query: '{query}', Page: {page})...")
    jobs = scrape_jobs(query, page)
    
    if not jobs:
        print("⚠️  No jobs scraped.")
        return 0
    
    print(f"\n=== PROCESSING {len(jobs)} JOBS ===\n")
    
    saved = 0
    for idx, job in enumerate(jobs, 1):
        print(f"--- JOB {idx}: {job['Job Title']} ---")
        
        job['Job ID'] = str(uuid.uuid4())[:8].upper()
        
        is_dup, dup_id = is_duplicate(job)
        if is_dup:
            print(f"❌ Duplicate (dup of {dup_id})")
            continue
        
        print("⚙️  Running parallel analysis...")
        try:
            result = await process_job_parallel(job)
            print(f"✅ Analysis: Skills & Company extracted")
            job.update(result)
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            continue
        
        # 🔥 NEW: CALCULATE SCORE (simple for now, enhance later)
        score = 75 + random.uniform(-10, 25)  # Demo: 65-100 range
        print(f"📊 Calculated score: {score:.1f}/100")
        
        # 🔥 NEW: WHATSAPP ALERT (non-blocking!)
        try:
            alert_sent = notifier.send_job_alert(job, score)
            if alert_sent:
                job['WhatsApp Alert'] = 'Sent'
                job['Alert Score'] = f"{score:.1f}"
                print("📱 WHATSAPP ALERT SENT! 🚨")
            else:
                job['WhatsApp Alert'] = 'Skipped/Low score'
        except Exception as e:
            print(f"⚠️ WhatsApp skipped (non-blocking): {e}")
            job['WhatsApp Alert'] = 'Error'
        
        job['Date Scraped'] = time.strftime("%Y-%m-%d")
        job['Verification Status'] = 'Pending'
        job['Priority Level'] = 'Medium'
        

        
        try:
            manager.append_job(job)
            saved += 1
            print(f"💾 Saved to Sheets (ID: {job['Job ID']})")
        except Exception as e:
            print(f"❌ Save error: {e}")
        
        print()
    
    print(f"✅ Round complete: {saved}/{len(jobs)} saved\n")
    return saved


async def orchestrate_batch(target_jobs: int = 30):
    """Loop through queries + pages until target reached."""
    print(f"\n🎯 TARGET: {target_jobs} new jobs\n")
    
    total_saved = 0
    query_idx = 0
    page = 1
    max_attempts = 50  # Prevent infinite loop
    attempt = 0
    
    while total_saved < target_jobs and attempt < max_attempts:
        query = QUERIES[query_idx % len(QUERIES)]
        
        saved = await orchestrate(query, page)
        total_saved += saved
        
        # Progress
        progress = (total_saved / target_jobs) * 100
        print(f"📊 Progress: {total_saved}/{target_jobs} ({progress:.0f}%)\n")
        
        if total_saved >= target_jobs:
            break
        
        # Rotate: next query after 2 pages, then next page
        page += 1
        if page > 3:  # Max 3 pages per query
            page = 1
            query_idx += 1
        
        time.sleep(2)  # Rate limit
        attempt += 1
    
    print(f"\n🎉 BATCH COMPLETE: {total_saved}/{target_jobs} jobs saved!\n")

if __name__ == "__main__":
    # Batch mode (auto-loop)
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    
    asyncio.run(orchestrate_batch(target))
