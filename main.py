import logging
import pandas as pd
import json
import os
import requests
import asyncio
from jobspy import scrape_jobs
from datetime import datetime

# --- CONFIGURATION ---
# 1. Search Terms: Broader scope for a graduate/junior
SEARCH_TERMS = [
    "Java Developer", 
    "Junior Software Engineer", 
    "Graduate Developer", 
    "Backend Developer"
]

LOCATION = "Australia"
RESULTS_PER_TERM = 10  # Keep low to avoid detection (4 terms x 10 = 40 max jobs)
HISTORY_FILE = "job_history.json"
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["CHAT_ID"]

# 2. Filters
# Exclude these strictly (Visa hurdles)
CITIZENSHIP_KEYWORDS = [
    "australian citizen", "citizenship required", "citizens only",
    "must be australian", "must be a citizen", "citizen of australia",
    "permanent resident", "pr or citizen", "security clearance", 
    "nv1", "baseline", "defence"
]

# Exclude Senior roles (Student protection)
SENIORITY_KEYWORDS = ["senior", "lead", "principal", "staff", "manager", "head of", "5+ years", "7+ years"]

# Remote Validation
REMOTE_KEYWORDS = ["remote", "work from home", "wfh", "anywhere", "virtual", "100% remote"]

# Tech Stack Detection
TECH_KEYWORDS = [
    'Spring Boot', 'Spring', 'Hibernate', 'AWS', 'Azure', 'GCP', 'Docker', 
    'Kubernetes', 'React', 'Angular', 'Vue', 'Node.js', 'SQL', 'PostgreSQL', 
    'MongoDB', 'Redis', 'Kafka', 'CI/CD', 'Git', 'Maven', 'Gradle'
]

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
    # Keep file size manageable
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-1000:], f)

def extract_tech_stack(description):
    found = []
    desc_lower = description.lower()
    # Check for keywords
    for tech in TECH_KEYWORDS:
        # Simple check: is the tech word in the description?
        if tech.lower() in desc_lower:
            found.append(tech)
    # Return top 5 to keep message clean
    return ', '.join(found[:5]) if found else 'Not specified'

async def main():
    print(f"🚀 Starting Job Hunt Routine...")
    
    all_jobs = pd.DataFrame()
    
    # 1. Loop through search terms
    for term in SEARCH_TERMS:
        print(f"🔍 Searching for '{term}'...")
        try:
            jobs = scrape_jobs(
                site_name=["indeed", "glassdoor"], 
                search_term=term,
                location=LOCATION,
                results_wanted=RESULTS_PER_TERM,
                country_indeed='australia' # FIXED: Full country name required
            )
            if not jobs.empty:
                all_jobs = pd.concat([all_jobs, jobs], ignore_index=True)
        except Exception as e:
            print(f"⚠️ Error searching '{term}': {e}")
            continue

    if all_jobs.empty:
        print("❌ No raw jobs found this run.")
        return

    # Remove duplicates (same job appearing in 'Java Developer' and 'Backend Developer')
    if 'id' in all_jobs.columns:
        all_jobs = all_jobs.drop_duplicates(subset=['id'], keep='first')
    else:
        # Fallback if ID is missing
        all_jobs = all_jobs.drop_duplicates(subset=['job_url'], keep='first')

    print(f"✅ Found {len(all_jobs)} unique raw jobs. Filtering...")

    history = load_history()
    darwin_jobs = []
    remote_jobs = []
    
    for index, job in all_jobs.iterrows():
        title = str(job.get('title', 'Unknown Role'))
        company = str(job.get('company', 'Unknown Company'))
        description = str(job.get('description', '')).lower()
        location = str(job.get('location', '')).lower()
        job_url = job.get('job_url', 'N/A')
        job_id = job.get('id', job_url)

        # --- FILTER 1: HISTORY ---
        if job_id in history:
            continue

        # --- FILTER 2: CITIZENSHIP ---
        if any(keyword in description for keyword in CITIZENSHIP_KEYWORDS):
            continue

        # --- FILTER 3: SENIORITY (Student Check) ---
        if any(keyword in title.lower() for keyword in SENIORITY_KEYWORDS):
            continue

        # --- FILTER 4: LOCATION & TYPE ---
        is_darwin = "darwin" in location or "northern territory" in location or "nt" in location
        is_remote = any(k in description or k in location for k in REMOTE_KEYWORDS)
        
        # Tech Stack Extraction
        tech_stack = extract_tech_stack(description)
        
        formatted_job = (
            f"*{title}*\n"
            f"🏢 {company}\n"
            f"📍 {job.get('location')}\n"
            f"💻 Tech: {tech_stack}\n"
            f"🔗 [Apply Here]({job_url})"
        )

        if is_darwin:
            darwin_jobs.append(formatted_job)
            history.append(job_id)
        elif is_remote:
            remote_jobs.append(formatted_job)
            history.append(job_id)
        # Else: It's an onsite job outside Darwin (e.g., Sydney Office) -> IGNORE

    # --- NOTIFICATION ---
    if darwin_jobs or remote_jobs:
        # 1. Send Darwin Jobs
        if darwin_jobs:
            msg = "🐊 *DARWIN / NT JOBS (All Types)*\n━━━━━━━━━━━━━━━━━━\n" + "\n\n".join(darwin_jobs)
            send_telegram(msg)
            
        # 2. Send Remote Jobs
        if remote_jobs:
            msg = "🌏 *REMOTE JOBS (Rest of AU)*\n━━━━━━━━━━━━━━━━━━\n" + "\n\n".join(remote_jobs)
            send_telegram(msg)
            
        # 3. Send Summary
        summary = (
            f"📊 *Job Hunt Summary*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🐊 Darwin Found: {len(darwin_jobs)}\n"
            f"🌏 Remote Found: {len(remote_jobs)}\n"
            f"🗑️ Filtered Out: {len(all_jobs) - (len(darwin_jobs) + len(remote_jobs))} (Visa/Senior/Onsite)"
        )
        send_telegram(summary)
        
        save_history(history)
        print(f"🚀 Sent alerts for {len(darwin_jobs) + len(remote_jobs)} jobs.")
    else:
        print("No matching jobs found after filtering.")

if __name__ == "__main__":
    asyncio.run(main())