"""
WhatsApp Webhook Server - WITH SHEETS SAVING
"""
from flask import Flask, request
import sys
from pathlib import Path
import json
import time
import uuid

sys.path.insert(0, str(Path(__file__).parent))
from utils.whatsapp_notifier import command_handler
from utils.sheets_manager import manager
from utils.duplicate_detector import is_duplicate

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
    """Run command + save jobs to Sheets."""
    from agents.job_scraper import scrape_jobs
    import random
    
    cmd = command_handler.parse_command(message)
    if not cmd['is_command']:
        return
    
    print(f"📱 Command: {cmd}")
    queries = [f"{cmd['keywords'][0]} {cmd['location']}", f"{cmd['keywords'][0]} remote"]
    
    saved_count = 0
    for query in queries[:2]:
        print(f"🔍 {query}")
        try:
            jobs = scrape_jobs(query, 1)
            for job in jobs[:3]:
                # Dedupe check
                is_dup, dup_id = is_duplicate(job)
                if is_dup:
                    print(f"❌ Duplicate: {dup_id}")
                    continue
                
                # Add metadata
                job['Job ID'] = str(uuid.uuid4())[:8].upper()
                job['Date Scraped'] = time.strftime("%Y-%m-%d")
                score = 75 + random.uniform(-10, 25)
                job['Match Score'] = f"{score:.0f}"
                
                # Send alert if high score
                if score >= 85:
                    command_handler.notifier.send_job_alert(job, score)
                
                # SAVE TO SHEETS
                try:
                    manager.append_job(job)
                    saved_count += 1
                    print(f"💾 Saved: {job['Job Title'][:30]}... (ID: {job['Job ID']})")
                except Exception as e:
                    print(f"❌ Sheets error: {e}")
        except Exception as e:
            print(f"❌ Scrape error: {e}")
    
    print(f"\n✅ Saved {saved_count} jobs to Sheets!\n")
    command_handler.notifier.send_message(
        command_handler.recipient_phone,
        f"✅ Found {saved_count} jobs! Check your Google Sheets 📊"
    )

@app.route('/webhook/whatsapp', methods=['GET'])
def verify_webhook():
    """Meta verification endpoint."""
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == "job_hunter_token":
        return challenge
    return "Invalid", 403

if __name__ == "__main__":
    print("🚀 WhatsApp Webhook Server READY on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
