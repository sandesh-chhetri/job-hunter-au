"""
Job Hunter AU - Automated IT Job Scraper for Australia

This module is the core scraper that:
1. Searches for IT jobs on Indeed and Google Jobs
2. Filters jobs based on relevance and eligibility criteria
3. Sends real-time alerts via Telegram
4. Maintains job history to prevent duplicate alerts

Target: Jobs relevant for Permanent Residency (PR) pathways in Australia
"""
import logging
import pandas as pd
import json
import os
import requests
import time
import re
from datetime import datetime
from jobspy import scrape_jobs
import config

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File paths and Telegram configuration
HISTORY_FILE = "job_history.json"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_IDS = [x.strip() for x in os.environ.get("CHAT_ID", "").split(",") if x.strip()]

def load_history():
    """
    Load job history from JSON file.
    
    Returns:
        list: List of previously seen job entries, or empty list if file doesn't exist
    """
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_history(history):
    """
    Save job history to JSON file, keeping only the last 1000 entries.
    
    Args:
        history (list): List of job entries to save
    """
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-1000:], f, indent=2)

def send_telegram(message):
    """
    Send a message to all configured Telegram chat IDs.
    
    Args:
        message (str): Message to send (supports Markdown formatting)
    """
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
            time.sleep(1)  # Rate limiting to be respectful to Telegram API
        except Exception as e:
            logger.error(f"❌ Failed to send to {chat_id}: {e}")

def matches_keywords(text, keywords):
    """
    Safely check if any keywords are present in the text.
    
    Uses word boundaries (\\b) for short abbreviations (<=3 chars) to prevent
    substring matching (e.g., "nt" won't match "Centre").
    
    Args:
        text (str): Text to search within
        keywords (list): List of keywords to search for
        
    Returns:
        bool: True if any keyword is found in the text
    """
    text_lower = text.lower()
    for kw in keywords:
        kw_lower = kw.lower()
        if len(kw_lower) <= 3:
            # Use regex for short words to prevent substring matching
            if re.search(r'\b' + re.escape(kw_lower) + r'\b', text_lower):
                return True
        else:
            # Normal substring match for longer words
            if kw_lower in text_lower:
                return True
    return False
    
def run_scraper():
    """
    Main scraper function that searches, filters, and alerts for new IT jobs.
    
    Workflow:
    1. Scrape jobs from Indeed and Google for each search term
    2. Remove duplicates from current run
    3. Filter against job history to find new jobs
    4. Apply blacklist and keyword filters
    5. Categorize by location (Darwin, Remote, Other)
    6. Send Telegram alerts for new matching jobs
    7. Update job history
    """
    logger.info("🚀 Starting Job Hunt...")
    
    all_jobs = pd.DataFrame()
    
    # Step 1: Scrape jobs for each search term
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

    # Step 2: Remove duplicates from current run
    if 'job_url' in all_jobs.columns:
        all_jobs = all_jobs.drop_duplicates(subset=['job_url'], keep='first')
    
    logger.info(f"✅ Found {len(all_jobs)} raw jobs. Filtering...")

    # Step 3: Load job history to identify new jobs
    history = load_history()
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
        
        # Step 4: Apply filters
        # Filter A: Skip if already seen
        if job_url in seen_urls:
            continue
            
        # Filter B: Skip if contains blacklist keywords (senior, citizenship, etc.)
        if matches_keywords(title, config.BLACKLIST_KEYWORDS) or matches_keywords(description, config.BLACKLIST_KEYWORDS):
            continue
            
        # Filter C: Must contain at least one required tech keyword
        full_text = title + " " + description
        if not matches_keywords(full_text, config.REQUIRED_KEYWORDS):
            continue

        # Step 5: Determine job location type
        is_darwin = matches_keywords(location, config.DARWIN_LOCATION_TERMS)
        is_remote = matches_keywords(description + " " + location, config.REMOTE_TERMS)
        
        # Step 6: Apply location-based filtering logic
        # - Darwin jobs: Accept all (flexible criteria)
        # - Remote jobs: Accept anywhere in Australia
        # - Other jobs: Only accept if part-time
        
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

    # Step 7: Send Telegram alerts for new matching jobs
    all_jobs_to_alert = []
    all_jobs_to_alert.extend(darwin_jobs)
    all_jobs_to_alert.extend(remote_jobs)
    all_jobs_to_alert.extend(other_jobs)
    
    if all_jobs_to_alert:
        logger.info(f"💌 Sending {len(all_jobs_to_alert)} alerts...")
        intro = f"👋 *Found {len(all_jobs_to_alert)} new jobs for you!*"
        send_telegram(intro)
        
        # Send alerts by category
        if darwin_jobs:
            send_telegram("🐊 *NEW DARWIN JOBS*\n" + "\n\n".join(darwin_jobs))
        
        if remote_jobs:
            send_telegram("🌏 *NEW REMOTE JOBS*\n" + "\n\n".join(remote_jobs))
        
        if other_jobs:
            send_telegram("💼 *NEW PART-TIME JOBS*\n" + "\n\n".join(other_jobs))
            
        # Step 8: Update job history
        history.extend(new_history_entries)
        save_history(history)
        logger.info("💾 History updated.")
    else:
        logger.info("😴 No new matching jobs found.")

if __name__ == "__main__":
    run_scraper()
