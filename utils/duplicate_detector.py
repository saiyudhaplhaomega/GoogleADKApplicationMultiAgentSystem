"""
Duplicate Detector - OPTION B
Checks Sheets for duplicates BUT allows saving anyway (configurable)
"""
import difflib
from typing import Dict, Any, List
from utils.sheets_manager import manager

DUPE_THRESHOLD = 0.90
ALLOW_DUPLICATE_SAVES = True  # NEW: Set to False to block duplicates

def is_duplicate(new_job: Dict[str, Any], check_only: bool = False) -> tuple[bool, str]:
    """
    Check if job is duplicate (Job Title + Company Name match).
    
    Args:
        new_job: Job dict to check
        check_only: If True, return duplicate status but DON'T block save
                   If False, block saves (old behavior)
    
    Returns:
        (is_dup: bool, dup_id: str)
    """
    try:
        records = manager.sheet.get_all_records()
        
        if not records:
            return False, ''
        
        new_title = new_job.get('Job Title', '').strip().lower()
        new_company = new_job.get('Company Name', '').strip().lower()
        
        if not new_title or not new_company:
            return False, ''
        
        found_dup = False
        dup_id = ''
        
        for record in records:
            old_title = record.get('Job Title', '').strip().lower()
            old_company = record.get('Company Name', '').strip().lower()
            old_job_id = record.get('Job ID', '')
            
            # Exact match: Title + Company
            if new_title == old_title and new_company == old_company and old_job_id:
                found_dup = True
                dup_id = old_job_id
                break
            
            # Fuzzy match: Title + Company both >90%
            if old_title and old_company:
                title_sim = difflib.SequenceMatcher(None, new_title, old_title).ratio()
                comp_sim = difflib.SequenceMatcher(None, new_company, old_company).ratio()
                
                if title_sim > DUPE_THRESHOLD and comp_sim > DUPE_THRESHOLD and old_job_id:
                    found_dup = True
                    dup_id = old_job_id
                    break
        
        # NEW LOGIC:
        if found_dup:
            if check_only or ALLOW_DUPLICATE_SAVES:
                # Log but don't block
                print(f"ℹ️ Duplicate found (dup of {dup_id}) but ALLOWING save")
                return False, ''  # Return False = allow save
            else:
                # Block save (old behavior)
                print(f"❌ Duplicate blocked (dup of {dup_id})")
                return True, dup_id
        
        return False, ''
        
    except Exception as e:
        print(f"❌ Dup check error: {e}")
        return False, ''


if __name__ == "__main__":
    test = {"Job Title": "Senior Python Dev", "Company Name": "Siemens"}
    print("Dup?", is_duplicate(test))
    print("With check_only?", is_duplicate(test, check_only=True))
