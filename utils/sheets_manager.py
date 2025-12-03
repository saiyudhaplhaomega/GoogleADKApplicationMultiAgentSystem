import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # Root

import gspread
from google.oauth2.service_account import Credentials
from config.config import COLUMNS, SHEETS_ID, GOOGLE_SHEETS_CREDENTIALS_PATH

from typing import Dict, Any, List
import pandas as pd
from pathlib import Path

class SheetsManager:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS_PATH, scopes=scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(SHEETS_ID).sheet1
        self.ensure_headers()

    def ensure_headers(self):
        """Set 57 columns if missing."""
        try:
            if self.sheet.row_count == 0:
                self.sheet.append_row(COLUMNS)
            else:
                current_headers = self.sheet.row_values(1)
                if current_headers != COLUMNS:
                    self.sheet.clear()
                    self.sheet.append_row(COLUMNS)
            print("Headers OK")
        except Exception as e:
            print(f"Sheets error: {e}")

    def append_job(self, job_data: Dict[str, Any]):
        """Append row, fill missing cols with ''."""
        try:
            row = []
            for col in COLUMNS:
                row.append(job_data.get(col, ''))
            self.sheet.append_row(row)
            print(f"Appended job {job_data.get('Job ID', 'Unknown')}")
        except Exception as e:
            print(f"Append error: {e}")

    def get_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Read recent jobs as list[dict]."""
        try:
            records = self.sheet.get_all_records()
            return records[-limit:] if records else []
        except Exception as e:
            print(f"Read error: {e}")
            return []

    def update_cell(self, row: int, col: str, value: Any):
        """Update specific cell."""
        try:
            col_idx = COLUMNS.index(col) + 1
            self.sheet.update_cell(row, col_idx, value)
        except Exception as e:
            print(f"Update error: {e}")

# Singleton
manager = SheetsManager()

if __name__ == "__main__":
    test_job = {"Job ID": "TEST1", "Job Title": "Test Job", "Date Scraped": "2025-12-02"}
    manager.append_job(test_job)
    print("Sheets ready!")
