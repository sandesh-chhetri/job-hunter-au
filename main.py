import logging
import pandas as pd
import json
import os
import requests
import asyncio
import sys
from jobspy import scrape_jobs
from datetime import datetime

# --- CONFIGURATION ---
# 1. Search Terms
SEARCH_TERMS = [
    # Core Java Roles
    "Java Developer", 
    "Junior Java Developer",
    "Backend Developer",
    
    # Generic Entry Level
    "Junior Software Engineer", 
    "Graduate Developer", 
    "Entry Level Software Engineer",
    "Associate Software Engineer",
    
    # Broader Titles (Good for getting foot in the door)
    "Software Developer",
    "Programmer",
    "Application Support Analyst",  # Often involves Java debugging
    "Junior Full Stack Developer"
]

# Reduce results per term slightly to keep total run time safe
RESULTS_PER_TERM = 10

LOCATION = "Australia"
RESULTS_PER_TERM = 10  # Keep low to avoid detection
HISTORY_FILE = "job_history.json"
# For testing, use test values if environment variables are not set
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "test_token")

# Split the string by commas to get a list of IDs
TELEGRAM_CHAT_IDS = [x.strip() for x in os.environ.get("CHAT_ID", "test_chat").split(",") if x.strip()]

# 2. Filters
CITIZENSHIP_KEYWORDS = [
    "australian citizen", "citizenship required", "citizens only",
    "must be australian", "must be a citizen", "citizen of australia",
    "permanent resident", "pr or citizen", "security clearance", 
    "nv1", "baseline", "defence"
]

SENIORITY_KEYWORDS = ["senior", "lead", "principal", "staff", "manager", "head of", "5+ years", "7+ years"]

REMOTE_KEYWORDS = ["remote", "work from home", "wfh", "anywhere", "virtual", "100% remote"]

TECH_KEYWORDS = [
    'Spring Boot', 'Spring', 'Hibernate', 'AWS', 'Azure', 'GCP', 'Docker', 
    'Kubernetes', 'React', 'Angular', 'Vue', 'Node.js', 'SQL', 'PostgreSQL', 
    'MongoDB', 'Redis', 'Kafka', 'CI/CD', 'Git', 'Maven', 'Gradle'
]

# AWS reposting blacklist - Targeted to block only AWS PACE jobs
AWS_BLACKLIST = [
    "prototyping engineer", "pace", "apj prototyping", 
    "aws web services", "amazon web services",
    "aws prototyping", "amazon prototyping", "aws pace", "amazon pace"
]

# Java-specific technology filter
JAVA_KEYWORDS = [
    'Java', 'Spring', 'Hibernate', 'Maven', 'Gradle', 'JPA', 
    'REST', 'Microservices', 'JDBC', 'JVM', 'J2EE', 'Servlet',
    'JSP', 'Struts', 'JSF', 'EJB', 'JMS', 'JNDI'
]
# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    for chat_id in TELEGRAM_CHAT_IDS:
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        try:
            requests.post(url, json=payload)
            print(f"Sent to ID: {chat_id}")
        except Exception as e:
            print(f"Error sending telegram to {chat_id}: {e}")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-1000:], f)

def is_duplicate_job(title, company, location, history):
    """Enhanced duplicate detection using title+company+location"""
    job_key = f"{title.lower().strip()}|{company.lower().strip()}|{location.lower().strip()}"
    return job_key in history

def add_to_history(title, company, location, history):
    """Add job to history with enhanced key and timestamp"""
    job_key = f"{title.lower().strip()}|{company.lower().strip()}|{location.lower().strip()}|{datetime.now().isoformat()}"
    history.append(job_key)

def add_to_history_on_prompt(title, company, location, history):
    """Add job to history only when prompted (for telegram bot)"""
    job_key = f"{title.lower().strip()}|{company.lower().strip()}|{location.lower().strip()}|{datetime.now().isoformat()}"
    history.append(job_key)

def add_all_to_history(title, company, location, history):
    """Add job to history without filtering (for testing)"""
    job_key = f"{title.lower().strip()}|{company.lower().strip()}|{location.lower().strip()}|{datetime.now().isoformat()}"
    history.append(job_key)

def has_java_technologies(description):
    """Check if job description mentions Java technologies"""
    desc_lower = description.lower()
    return any(tech.lower() in desc_lower for tech in JAVA_KEYWORDS)
def extract_tech_stack(description):
    found = []
    desc_lower = description.lower()
    for tech in TECH_KEYWORDS:
        if tech.lower() in desc_lower:
            found.append(tech)
    return ', '.join(found[:5]) if found else 'Not specified'

async def main():
    # Check if we just want the report
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        from job_history_reviewer import analyze_job_history
        report = analyze_job_history()
        send_telegram(f"📜 *JOB HISTORY REPORT*\n{report}")
        return

    print(f"🚀 Starting Job Hunt Routine...")
    
    all_jobs = pd.DataFrame()
    
    # 1. Loop through search terms
    for term in SEARCH_TERMS:
        print(f"🔍 Searching for '{term}'...")
        try:
            jobs = scrape_jobs(
                site_name=["indeed", "google"],
                search_term=term,
                location=LOCATION,
                results_wanted=RESULTS_PER_TERM,
                country_indeed='australia'
            )
            if not jobs.empty:
                all_jobs = pd.concat([all_jobs, jobs], ignore_index=True)
        except Exception as e:
            print(f"⚠️ Error searching '{term}': {e}")
            continue

    if all_jobs.empty:
        print("❌ No raw jobs found this run.")
        return

    # Remove duplicates
    if 'id' in all_jobs.columns:
        all_jobs = all_jobs.drop_duplicates(subset=['id'], keep='first')
    else:
        all_jobs = all_jobs.drop_duplicates(subset=['job_url'], keep='first')

    print(f"✅ Found {len(all_jobs)} unique raw jobs. Filtering...")

    history = load_history()
    # Extract just the keys for comparison (ignoring timestamps)
    existing_keys = [k.split('|')[0:3] for k in history]
    existing_keys = ["|".join(k) for k in existing_keys]

    darwin_jobs = []
    remote_jobs = []
    
    for _, job in all_jobs.iterrows():
        title = str(job.get('title', 'Unknown'))
        company = str(job.get('company', 'Unknown'))
        location = str(job.get('location', '')).lower()
        description = str(job.get('description', '')).lower()
        
        job_key = f"{title.lower().strip()}|{company.lower().strip()}|{location.lower().strip()}"
        
        if job_key in existing_keys:
            continue
        if any(k in description for k in CITIZENSHIP_KEYWORDS):
            continue
        if any(k in title.lower() for k in SENIORITY_KEYWORDS):
            continue
        if not any(k.lower() in description for k in JAVA_KEYWORDS):
            continue

        # --- ADD THIS BLOCK ---
        # Check Blacklist (AWS Spam)
        if any(keyword in title.lower() for keyword in AWS_BLACKLIST):
            print(f"🗑️ Dropped '{title}': Blacklisted keyword")
            continue
        # ----------------------

        is_darwin = any(k in location for k in ["darwin", "nt", "northern territory"])
        is_remote = any(k in description or k in location for k in REMOTE_KEYWORDS)
        
        if is_darwin or is_remote:
            formatted = f"*{title}*\n🏢 {company}\n📍 {location}\n🔗 [Apply]({job.get('job_url')})"
            if is_darwin: darwin_jobs.append(formatted)
            else: remote_jobs.append(formatted)
            
            # Add to history with timestamp
            history.append(f"{job_key}|{datetime.now().isoformat()}")

    # Send alerts only for NEW jobs
    if darwin_jobs:
        send_telegram("🐊 *NEW DARWIN JOBS*\n" + "\n\n".join(darwin_jobs))
    if remote_jobs:
        send_telegram("🌏 *NEW REMOTE JOBS*\n" + "\n\n".join(remote_jobs))
    
    if darwin_jobs or remote_jobs:
        save_history(history)

if __name__ == "__main__":
    asyncio.run(main())