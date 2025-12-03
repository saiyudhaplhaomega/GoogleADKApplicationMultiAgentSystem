# test_direct.py
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import time

PHONE_ID = "808984875642633"
ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
TO_PHONE = "4915906396002"  # YOUR NUMBER

url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
data = {
    "messaging_product": "whatsapp",
    "to": TO_PHONE,
    "type": "text",
    "text": {"body": "🚨 TEST: Job hunter is LIVE!"}
}
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}

resp = requests.post(url, json=data, headers=headers)
print("RESPONSE:", resp.json())

if resp.status_code == 200:
    msg_id = resp.json()['messages'][0]['id']
    print(f"✅ SENT! Msg ID: {msg_id}")
    print("Check WhatsApp NOW!")
else:
    print("❌ FAILED:", resp.text)
