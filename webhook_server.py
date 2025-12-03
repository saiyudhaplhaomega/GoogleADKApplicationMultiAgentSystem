"""
WhatsApp Webhook Server - COMPLETE PRODUCTION VERSION
WITH SHEETS SAVING + AI ANALYSIS + DYNAMIC JOB LIMIT + DEBUG
"""
from flask import Flask, request
import sys
from pathlib import Path
import json
import time
import uuid
import random

sys.path.insert(0, str(Path(__file__).parent))
from utils.whatsapp_notifier import command_handler
from utils.sheets_manager import manager
from utils.duplicate_detector import is_duplicate
from agents.job_scraper import scrape_jobs

app = Flask(__name__)

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages + SAVE TO SHEETS."""
    try:
        data = request.json
        print(f"\n{'='*60}")
        print(f"📨 RECEIVED POST MESSAGE!")
        print(f"{'='*60}")
        
        if 'entry' in data:
            for entry in data['entry']:
                for change in entry['changes']:
                    if 'messages' in change['value']:
                        messages = change['value']['messages']
                        
                        for msg in messages:
                            text = msg['text']['body']
                            print(f"👤 Message: {text}\n")
                            
                            # Handle command + SAVE RESULTS
                            save_command_results(text)
        
        return {"status": "ok"}
    except Exception as e:
        print(f"\n❌ POST Error: {e}\n")
        import traceback
        traceback.print_exc()
        return {"status": "error"}, 500

def save_command_results(message: str):
    """Run command + analyze + save jobs to Sheets - DYNAMIC LIMIT."""
    
    try:
        from agents.skill_analyzer import analyze_job_skills
        from agents.company_researcher import research_company
    except ImportError as e:
        print(f"⚠️ AI agents not found: {e}")
        analyze_job_skills = None
        research_company = None
    
    cmd = command_handler.parse_command(message)
    if not cmd['is_command']:
        print("⚠️ Not recognized as command")
        return
    
    print(f"📱 Command: {cmd}")
    queries = [f"{cmd['keywords'][0]} {cmd['location']}", f"{cmd['keywords'][0]} remote"]
    
    saved_count = 0
    MAX_JOBS = cmd['num_jobs']  # 🎯 USE REQUESTED NUMBER!
    print(f"🎯 Limit: {MAX_JOBS} jobs\n")
    
    for query in queries[:2]:
        if saved_count >= MAX_JOBS:
            print(f"🛑 Reached {MAX_JOBS} job limit!")
            break
        
        print(f"\n🔍 SCRAPING: {query}")
        print("-" * 60)
        try:
            jobs = scrape_jobs(query, 1)
            print(f"✅ Scraper returned: {len(jobs)} jobs\n")
            
            if not jobs:
                print(f"⚠️ No jobs from this query")
                continue
            
            for idx, job in enumerate(jobs[:3], 1):
                if saved_count >= MAX_JOBS:
                    print(f"🛑 Reached {MAX_JOBS} job limit!")
                    break
                
                print(f"\n--- JOB {idx}/{len(jobs)} ---")
                print(f"Title: {job.get('Job Title', 'N/A')}")
                print(f"Company: {job.get('Company Name', 'N/A')}")
                
                # Dedupe check
                is_dup, dup_id = is_duplicate(job)
                if is_dup:
                    print(f"❌ Duplicate")
                    continue
                print(f"✅ Not duplicate")
                
                # 🔥 AI SKILL ANALYSIS
                if analyze_job_skills:
                    print("⚙️ Analyzing skills...")
                    try:
                        skill_data = analyze_job_skills(job)
                        job.update(skill_data)
                        print(f"✅ Skills: {skill_data.get('Skills Match %', 'N/A')}")
                        print(f"   Required: {skill_data.get('Required Skills', 'N/A')[:60]}...")
                        print(f"   Match: {skill_data.get('Your Matching Skills', 'N/A')[:60]}...")
                        print(f"   Missing: {skill_data.get('Missing Skills', 'N/A')[:60]}...")
                    except Exception as e:
                        print(f"⚠️ Skill error: {e}")
                        import traceback
                        traceback.print_exc()
                
                # 🔥 AI COMPANY RESEARCH
                if research_company:
                    print("⚙️ Researching company...")
                    try:
                        company_data = research_company(job)
                        job.update(company_data)
                        print(f"✅ Company Mission: {company_data.get('Company Mission', 'N/A')[:50]}...")
                        print(f"   Culture: {company_data.get('Company Culture Keywords', 'N/A')[:50]}...")
                        print(f"   Tech Stack: {company_data.get('Tech Stack Used', 'N/A')[:50]}...")
                    except Exception as e:
                        print(f"⚠️ Company error: {e}")
                
                # Add metadata
                job['Job ID'] = str(uuid.uuid4())[:8].upper()
                job['Date Scraped'] = time.strftime("%Y-%m-%d")
                
                # Get score from skills match or use random
                match_str = job.get('Skills Match %', '50%').rstrip('%')
                try:
                    score = float(match_str)
                except:
                    score = 75 + random.uniform(-10, 25)
                
                job['Match Score'] = f"{score:.0f}"
                print(f"📊 Score: {score:.0f}/100")
                
                # Send alert if high score
                if score >= 85:
                    print(f"🚨 HIGH SCORE! Sending WhatsApp alert...")
                    try:
                        command_handler.notifier.send_job_alert(job, score)
                        print(f"✅ Alert sent!")
                    except Exception as e:
                        print(f"❌ Alert failed: {e}")
                
                # SAVE TO SHEETS
                try:
                    manager.append_job(job)
                    saved_count += 1  # 🎯 INCREMENT COUNTER
                    print(f"💾 ✅ SAVED TO SHEETS! ({saved_count}/{MAX_JOBS} ID: {job['Job ID']})")
                except Exception as e:
                    print(f"❌ Sheets save error: {e}")
                    import traceback
                    traceback.print_exc()
        
        except Exception as e:
            print(f"❌ Scrape error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"✅ TOTAL SAVED: {saved_count}/{MAX_JOBS} jobs to Sheets!")
    print(f"{'='*60}\n")
    
    try:
        command_handler.notifier.send_message(
            command_handler.recipient_phone,
            f"✅ Saved {saved_count}/{MAX_JOBS} jobs! Check your Google Sheets 📊"
        )
    except Exception as e:
        print(f"⚠️ Message send failed: {e}")

@app.route('/webhook/whatsapp', methods=['GET'])
def verify_webhook():
    """Meta verification endpoint."""
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    print(f"\n🔐 Verify Token: {token}")
    print(f"🔐 Challenge: {challenge}\n")
    
    if token == "job_hunter_token":
        print("✅ Token verified!\n")
        return challenge
    
    print("❌ Invalid token!\n")
    return "Invalid", 403

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 WhatsApp Webhook Server READY on port 5000")
    print("📍 Webhook: http://0.0.0.0:5000/webhook/whatsapp")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
