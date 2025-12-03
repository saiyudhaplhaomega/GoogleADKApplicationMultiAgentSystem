# final_test.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.whatsapp_notifier import notifier

test_job = {
    'Job Title': 'FINAL TEST - Senior Python Dev',
    'Company Name': 'TechCorp Berlin', 
    'Location': 'Berlin Remote',
    'Job URL': 'https://test.com/job123'
}

success = notifier.send_job_alert(test_job, 95)
print(f"🎉 {'✅ ALERT SENT!' if success else '❌ FAILED'}")
print("📱 Check +4915906396002 NOW!")
