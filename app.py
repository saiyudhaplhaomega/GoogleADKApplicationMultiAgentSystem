import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from flask import Flask, request
from utils.whatsapp_notifier import process_incoming_whatsapp
import asyncio

app = Flask(__name__)

@app.route('/webhook/whatsapp', methods=['POST'])
async def whatsapp_webhook():
    data = request.json
    message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    
    # Process command
    await process_incoming_whatsapp(message)
    
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(port=8000)
