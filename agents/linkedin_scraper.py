from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from typing import List, Dict

def scrape_linkedin(query: str) -> List[Dict]:
    """LinkedIn scraping (HIGH RISK - ToS violation, IP blocks likely)."""
    jobs = []
    
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0...")
        
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        
        # Navigate
        url = f"https://de.linkedin.com/jobs/search?keywords={query}&location=Germany"
        driver.get(url)
        time.sleep(3)
        
        # Wait for job cards
        wait = WebDriverWait(driver, 10)
        job_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "job-card")))
        
        for card in job_cards[:5]:
            try:
                title = card.find_element(By.CLASS_NAME, "job-title").text
                company = card.find_element(By.CLASS_NAME, "job-company").text
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                jobs.append({
                    "Job Portal": "LinkedIn",
                    "Job Title": title,
                    "Company Name": company,
                    "Location": "Germany",
                    "Remote Type": "Unknown",
                    "Job URL": link,
                    "Job Description": "",
                    "Date Scraped": time.strftime("%Y-%m-%d")
                })
            except:
                continue
        
        driver.quit()
        return jobs
    except Exception as e:
        print(f"LinkedIn scrape error: {e}")
        return []
