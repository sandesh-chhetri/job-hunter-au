import logging
import pandas as pd
import json
import os
import requests
import time
import re  # <-- ADDED: Required for the matches_keywords function
from datetime import datetime
from jobspy import scrape_jobs
import config  # Import our new config file

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HISTORY_FILE = "job_history.json"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_IDS = [x.strip() for x in os.environ.get("CHAT_ID", "").split(",") if x.strip()]

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_history(history):
    # Keep only the last 1000 entries to prevent the file from growing infinitely
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-1000:], f, indent=2)

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_IDS:
        logger.error("❌ Telegram credentials missing.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    for chat_id in TELEGRAM_CHAT_IDS:
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        try:
            requests.post(url, json=payload, timeout=10)
            logger.info(f"✅ Sent to chat ID: {chat_id}")
            time.sleep(1) # Be nice to Telegram API
        except Exception as e:
            logger.error(f"❌ Failed to send to {chat_id}: {e}")

def matches_keywords(text, keywords):
    """
    Safely checks if keywords are in the text.
    Uses word boundaries (\b) for short abbreviations to prevent substring matching.
    """
    text_lower = text.lower()
    for kw in keywords:
        kw_lower = kw.lower()
        if len(kw_lower) <= 3:
            # Use regex for short words (e.g., "nt", "qa", "sql", "sr") so they don't match inside larger words
            if re.search(r'\b' + re.escape(kw_lower) + r'\b', text_lower):
                return True
        else:
            # Normal substring match for longer words
            if kw_lower in text_lower:
                return True
    return False
    
def run_scraper():
    logger.info("🚀 Starting Job Hunt...")
    
    all_jobs = pd.DataFrame()
    
    # 1. Scrape for each search term
    for term in config.SEARCH_TERMS:
        logger.info(f"🔎 Searching: {term}")
        try:
            jobs = scrape_jobs(
                site_name=["indeed", "google"], # Removed glassdoor due to 403 blocking
                search_term=term,
                location=config.LOCATION,
                results_wanted=config.RESULTS_PER_TERM,
                country_indeed='australia'
            )
            if not jobs.empty:
                all_jobs = pd.concat([all_jobs, jobs], ignore_index=True)
        except Exception as e:
            logger.warning(f"⚠️ Error scraping '{term}': {e}")
            continue

    if all_jobs.empty:
        logger.info("❌ No jobs found this run.")
        return

    # 2. Filter Duplicates from this run
    # Drop duplicates based on URL or ID
    if 'job_url' in all_jobs.columns:
        all_jobs = all_jobs.drop_duplicates(subset=['job_url'], keep='first')
    
    logger.info(f"✅ Found {len(all_jobs)} raw jobs. Filtering...")

    # 3. Load History
    history = load_history()
    # Create a set of previously seen URLs for fast lookup
    seen_urls = {entry.get('url') for entry in history}
    
    new_history_entries = []
    darwin_jobs = []
    remote_jobs = []
    other_jobs = []

    for _, job in all_jobs.iterrows():
        title = str(job.get('title', 'Unknown'))
        company = str(job.get('company', 'Unknown'))
        location = str(job.get('location', '')).lower()
        description = str(job.get('description', '')).lower()
        job_url = str(job.get('job_url', ''))
        
        # --- FILTERS ---
        
        # A. Already seen?
        if job_url in seen_urls:
            continue
            
        # B. Blacklisted words (Senior, Citizen)?
        # <-- UPDATED: Now uses matches_keywords instead of the buggy any() loop
        if matches_keywords(title, config.BLACKLIST_KEYWORDS) or matches_keywords(description, config.BLACKLIST_KEYWORDS):
            continue
            
        # C. Must have tech keywords?
        # <-- UPDATED: Now uses matches_keywords
        full_text = title + " " + description
        if not matches_keywords(full_text, config.REQUIRED_KEYWORDS):
            continue

        # --- LOCATION AND WORK TYPE FILTERS ---
        
        # <-- UPDATED: Now uses matches_keywords to prevent "nt" matching "Centre"
        is_darwin = matches_keywords(location, config.DARWIN_LOCATION_TERMS)
        is_remote = matches_keywords(description + " " + location, config.REMOTE_TERMS)
        
        # D. Location-based filtering logic:
        # - If in Darwin: Accept all (flexible criteria)
        # - If outside Darwin: Must be remote or part-time
        # - If location is not specified: Assume remote or accept if it matches tech requirements
        
        if is_darwin:
            # Darwin jobs: Flexible criteria - accept if it passed previous filters
            formatted = f"*{title}*\n🏢 {company}\n📍 {location.title()}\n🔗 [Apply Here]({job_url})"
            darwin_jobs.append(formatted)
        elif is_remote:
            # Remote jobs outside Darwin: Accept if it passed previous filters
            formatted = f"*{title}*\n🏢 {company}\n📍 {location.title()} (Remote)\n🔗 [Apply Here]({job_url})"
            remote_jobs.append(formatted)
        else:
            # Non-remote, non-Darwin jobs: Only accept if part-time is mentioned
            if "part-time" in description.lower():
                formatted = f"*{title}*\n🏢 {company}\n📍 {location.title()} (Part-time)\n🔗 [Apply Here]({job_url})"
                other_jobs.append(formatted)
            else:
                # Skip non-remote, non-Darwin, non-part-time jobs
                continue

        # Prepare History Entry
        new_history_entries.append({
            "title": title,
            "company": company,
            "url": job_url,
            "scraped_at": datetime.now().isoformat()
        })

    # 4. Send Alerts
    all_jobs_to_alert = []
    all_jobs_to_alert.extend(darwin_jobs)
    all_jobs_to_alert.extend(remote_jobs)
    all_jobs_to_alert.extend(other_jobs)
    
    if all_jobs_to_alert:
        logger.info(f"💌 Sending {len(all_jobs_to_alert)} alerts...")
        intro = f"👋 *Found {len(all_jobs_to_alert)} new jobs for you!*"
        send_telegram(intro)
        
        # Send Darwin jobs first
        if darwin_jobs:
            send_telegram("🐊 *NEW DARWIN JOBS*\n" + "\n\n".join(darwin_jobs))
        
        # Send remote jobs
        if remote_jobs:
            send_telegram("🌏 *NEW REMOTE JOBS*\n" + "\n\n".join(remote_jobs))
        
        # Send other part-time jobs
        if other_jobs:
            send_telegram("💼 *NEW PART-TIME JOBS*\n" + "\n\n".join(other_jobs))
            
        # 5. Save History
        history.extend(new_history_entries)
        save_history(history)
        logger.info("💾 History updated.")
    else:
        logger.info("😴 No new matching jobs found.")

if __name__ == "__main__":
    run_scraper()