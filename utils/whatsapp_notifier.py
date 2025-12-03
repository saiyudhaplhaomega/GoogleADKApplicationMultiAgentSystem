# final_test.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import requests
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
RECIPIENT_PHONE = os.getenv("WHATSAPP_RECIPIENT", "4915906396002")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whatsapp_notifier")

class WhatsAppNotifier:
    def __init__(self):
        if not all([PHONE_ID, ACCESS_TOKEN]):
            logger.warning("⚠️ WhatsApp disabled - missing env vars")
            self.enabled = False
            return
        self.base_url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
        self.enabled = True
        logger.info("✅ WhatsAppNotifier ready")
    
    def send_message(self, to: str, message: str) -> Optional[str]:
        if not self.enabled:
            return None
        data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": message}}
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
        resp = requests.post(self.base_url, json=data, headers=headers, timeout=15)
        if resp.status_code == 200:
            msg_id = resp.json()['messages'][0]['id']
            logger.info(f"✅ WhatsApp SENT! ID: {msg_id}")
            return msg_id
        logger.error(f"❌ WhatsApp failed: {resp.text}")
        return None
    
    def format_job_alert(self, job: Dict[str, Any], score: float) -> str:
        title = job.get('Job Title', 'N/A')
        company = job.get('Company Name', 'N/A')
        location = job.get('Location', 'N/A')
        url = job.get('Job URL', 'N/A')
        return f"""🔥 JOB MATCH: {score:.0f}/100

{title} | {company} | {location}
Apply: {url}""".strip()
    
    def send_job_alert(self, job: Dict[str, Any], score: float) -> bool:
        if not self.enabled or score < 85:
            return False
        message = self.format_job_alert(job, score)
        return self.send_message(RECIPIENT_PHONE, message) is not None

notifier = WhatsAppNotifier()
