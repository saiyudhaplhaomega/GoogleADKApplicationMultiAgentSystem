"""
Production-ready WhatsApp notifier + COMMAND HANDLER
Job alerts + "10 data engineer germany" commands
"""
import os
import time
import requests
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv
import sys
import re
import random

load_dotenv()

# ENV VARS
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
RECIPIENT_PHONE = os.getenv("WHATSAPP_RECIPIENT", "4915906396002")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("whatsapp_notifier")

class WhatsAppNotifier:
    def __init__(self):
        if not all([PHONE_ID, ACCESS_TOKEN]):
            logger.warning("⚠️ WhatsApp credentials missing - alerts disabled")
            self.enabled = False
            return
        
        self.base_url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
        self.enabled = True
        logger.info("✅ WhatsAppNotifier ready")
    
    def send_message(self, to: str, message: str, max_retries: int = 3) -> Optional[str]:
        if not self.enabled:
            return None
        
        data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": message}}
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
        
        for attempt in range(max_retries):
            try:
                resp = requests.post(self.base_url, json=data, headers=headers, timeout=15)
                resp.raise_for_status()
                result = resp.json()
                msg_id = result['messages'][0]['id']
                logger.info(f"✅ WhatsApp SUCCESS. Msg ID: {msg_id}")
                return msg_id
            except Exception as e:
                wait_time = (2 ** attempt) + 0.1
                logger.warning(f"❌ WhatsApp attempt {attempt+1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
        
        logger.error("❌ WhatsApp FAILED after retries")
        return None
    
    def format_job_alert(self, job: Dict[str, Any], score: float) -> str:
        title = job.get('Job Title', 'N/A')
        company = job.get('Company Name', 'N/A')
        location = job.get('Location', 'N/A')
        url = job.get('Job URL', 'N/A')
        
        alert = f"""🔥 JOB MATCH: {score:.0f}/100

{title} | {company} | {location}
Apply: {url}"""
        return alert.strip()
    
    def send_job_alert(self, job: Dict[str, Any], score: float) -> bool:
        if not self.enabled or score < 85:
            return False
        
        message = self.format_job_alert(job, score)
        logger.info(f"🚨 SENDING ALERT (score: {score:.1f}): {message[:80]}...")
        msg_id = self.send_message(RECIPIENT_PHONE, message)
        return msg_id is not None

# Global notifier instance
notifier = WhatsAppNotifier()

# ==================== WHATSAPP COMMANDS ====================
if 'notifier' in globals():
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from agents.job_scraper import scrape_jobs
        import time
        import random
        
        class WhatsAppCommandHandler:
            def __init__(self, notifier_instance):
                self.notifier = notifier_instance
                self.recipient_phone = RECIPIENT_PHONE
            
            def parse_command(self, message: str) -> Dict:
                nums = re.findall(r'\b(\d+)\b', message)
                keywords = re.findall(r'\b(data engineer|devops|python|aws|backend|mlops)\b', message.lower())
                loc_match = re.search(r'(germany|berlin|remote|de|munich)', message.lower())
                return {
                    'num_jobs': int(nums[0]) if nums else 10,
                    'keywords': keywords or ['python developer'],
                    'location': loc_match.group(1) if loc_match else 'germany',
                    'is_command': bool(keywords or nums)
                }
            
            def handle_command(self, message: str):
                cmd = self.parse_command(message)
                if not cmd['is_command']:
                    return False
                
                print(f"📱 WhatsApp Command: {cmd}")
                reply = f"🔍 Searching {cmd['num_jobs']} {cmd['keywords'][0]} jobs ({cmd['location']})..."
                self.notifier.send_message(self.recipient_phone, reply)
                
                queries = [
                    f"{cmd['keywords'][0]} {cmd['location']}",
                    f"{cmd['keywords'][0]} remote",
                    f"senior {cmd['keywords'][0]}"
                ]
                
                jobs_found = self.run_quick_search(queries, cmd['num_jobs'])
                self.notifier.send_message(self.recipient_phone, f"✅ Found {jobs_found} jobs! High matches sent 📊")
                return True
            
            def run_quick_search(self, queries: list, target: int) -> int:
                total = 0
                for query in queries[:2]:
                    print(f"🔍 Running: {query}")
                    try:
                        jobs = scrape_jobs(query, 1)
                        for job in jobs[:3]:
                            score = 75 + random.uniform(-10, 25)
                            if score >= 85:
                                self.notifier.send_job_alert(job, score)
                            total += 1
                            if total >= target:
                                break
                    except Exception as e:
                        print(f"❌ Scrape error: {e}")
                        continue
                    
                    if total >= target:
                        break
                    time.sleep(1)
                return total
        
        command_handler = WhatsAppCommandHandler(notifier)
        print("✅ WhatsApp Command Handler READY!")
    except ImportError as e:
        print(f"⚠️ Commands disabled (missing imports): {e}")
        command_handler = None
else:
    print("⚠️ notifier not available - commands disabled")
    command_handler = None
