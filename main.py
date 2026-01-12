import logging
import pandas as pd
import json
import os
import requests
import asyncio
from jobspy import scrape_jobs
from datetime import datetime

# --- CONFIGURATION ---
SEARCH_TERM = "Java Developer"
LOCATION = "Australia"
RESULTS_WANTED = 20  # Keep low to avoid detection
HISTORY_FILE = "job_history.json"
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["CHAT_ID"]

# Filter Keywords
CITIZENSHIP_KEYWORDS = [
    "australian citizen", "citizenship required", "citizens only",
    "must be australian", "must be a citizen", "citizen of australia",
    "permanent resident", "pr or citizen", "security clearance", "nv1", "baseline"
]

REMOTE_KEYWORDS = ["remote", "work from home", "wfh", "anywhere", "virtual", "hybrid"]

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending telegram: {e}")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    # Keep only the last 500 jobs to save space
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-500:], f)

async def main():
    print(f"🔍 Searching for {SEARCH_TERM} in {LOCATION}...")
    
    # 1. Scrape Jobs (Indeed, LinkedIn, Glassdoor)
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "glassdoor"],
        search_term=SEARCH_TERM,
        location=LOCATION,
        results_wanted=RESULTS_WANTED,
        country_indeed='AU'
    )
    
    if jobs.empty:
        print("No jobs found this run.")
        return

    print(f"✅ Found {len(jobs)} raw jobs. Filtering...")

    # 2. Load History for De-duplication
    history = load_history()
    new_jobs_found = []
    
    # 3. Filter & Process
    for index, job in jobs.iterrows():
        title = str(job.get('title', '')).lower()
        description = str(job.get('description', '')).lower()
        location = str(job.get('location', '')).lower()
        job_url = job.get('job_url', 'N/A')
        job_id = job.get('id', job_url) # Use URL as ID if ID is missing

        # --- DEDUPLICATION FILTER ---
        if job_id in history:
            continue

        # --- CITIZENSHIP FILTER ---
        if any(keyword in description for keyword in CITIZENSHIP_KEYWORDS):
            continue

        # --- LOCATION STRATEGY ---
        # If Darwin: Keep it regardless of type
        # If NOT Darwin: Must be Remote/Hybrid
        is_darwin = "darwin" in location
        is_remote = any(k in description or k in location for k in REMOTE_KEYWORDS)
        
        if not is_darwin and not is_remote:
            continue

        # If we made it here, it's a MATCH!
        history.append(job_id)
        
        # Format Job for Telegram
        formatted_job = (
            f"*{job.get('title')}*\n"
            f"🏢 {job.get('company')}\n"
            f"📍 {job.get('location')}\n"
            f"🔗 [Apply Here]({job_url})"
        )
        new_jobs_found.append(formatted_job)

    # 4. Send Notifications
    if new_jobs_found:
        header = f"🔔 *Job Alerts: {len(new_jobs_found)} New Jobs*\n━━━━━━━━━━━━━━━━━━\n"
        # Telegram has a message limit, so we send in chunks if needed
        message_body = "\n\n".join(new_jobs_found)
        full_message = header + message_body
        
        # Simple split if too long (Telegram limit ~4096 chars)
        if len(full_message) > 4000:
            for chunk in new_jobs_found:
                 send_telegram(chunk)
        else:
            send_telegram(full_message)
            
        print(f"🚀 Sent {len(new_jobs_found)} alerts.")
        
        # 5. Save History
        save_history(history)
    else:
        print("No new matching jobs found after filtering.")

if __name__ == "__main__":
    asyncio.run(main())