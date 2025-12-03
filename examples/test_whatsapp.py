import sys
from pathlib import Path
import time  # Fixed
import os
from dotenv import load_dotenv
load_dotenv()
import requests

PHONE_ID = "808984875642633"
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")

def send_whatsapp(to: str, msg: str):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": msg}
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    resp = requests.post(url, json=data, headers=headers)  # Renamed var
    print(resp.json())
    return resp

resp = send_whatsapp("4915906396002", "Test fixed!")
msg_id = resp.json()['messages'][0]['id']
print(f"Msg ID: {msg_id}")
time.sleep(30)
status_res = requests.get(
    f"https://graph.facebook.com/v18.0/{msg_id}",
    params={"fields": "status,timestamp"},
    headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
)
print(status_res.json())  # Status!


#!/usr/bin/env python3
"""
TEST YOUR WHATSAPP ALERTS RIGHT NOW with your credentials.
"""
from utils.whatsapp_notifier import notifier

print("🧪 TESTING WHATSAPP WITH YOUR CREDENTIALS...")

# Real job example
test_job = {
    'job_title': 'Senior Python Developer (REMOTE)',
    'company_name': 'TechCorp Berlin GmbH',
    'location': 'Berlin, Germany (Remote OK)',
    'job_url': 'https://apply.techcorp.de/senior-python-2025',
    'skills_match_percent': '94%'
}

# TEST HIGH SCORE (will trigger)
success = notifier.send_job_alert(test_job, 94.5)

print(f"\n🎉 TEST RESULT: {'✅ SUCCESS' if success else '❌ FAILED (non-blocking)'}")
print("Check your WhatsApp now! 📱")

