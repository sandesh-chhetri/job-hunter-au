#!/usr/bin/env python3
"""
Job History Reviewer - Returns string for Telegram
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

HISTORY_FILE = "job_history.json"

def load_job_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def parse_job_key(job_key):
    try:
        parts = job_key.split("|")
        # Handle both old format (3 parts) and new format (4 parts)
        if len(parts) >= 3:
            return {
                "title": parts[0].strip(),
                "company": parts[1].strip(),
                "location": parts[2].strip(),
                "timestamp": parts[3] if len(parts) > 3 else None
            }
        return {"title": "Unknown", "company": "Unknown", "location": "Unknown", "timestamp": None}
    except ValueError:
        return {"title": "Unknown", "company": "Unknown", "location": "Unknown", "timestamp": None}

def analyze_job_history():
    """Analyze job history and return a formatted string"""
    history = load_job_history()
    current_time = datetime.now()
    cutoff_time = current_time - timedelta(days=14) # Changed to 2 weeks to match description
    
    filtered_jobs = []
    for job_key in history:
        job = parse_job_key(job_key)
        if job["timestamp"]:
            try:
                job_time = datetime.fromisoformat(job["timestamp"])
                if job_time >= cutoff_time:
                    filtered_jobs.append(job)
            except ValueError:
                filtered_jobs.append(job)
        else:
            # Include older jobs without timestamps if you want, or exclude them
            filtered_jobs.append(job)
            
    # Start building the report string
    output = []
    
    # Stats
    companies = defaultdict(list)
    locations = defaultdict(list)
    for job in filtered_jobs:
        companies[job["company"]].append(job)
        locations[job["location"]].append(job)

    output.append(f"📈 *Job Stats (Last 14 Days)*")
    output.append(f"Total Found: {len(filtered_jobs)}")
    output.append(f"Unique Companies: {len(companies)}\n")
    
    # Top Companies
    output.append("*🏢 TOP COMPANIES*")
    sorted_companies = sorted(companies.items(), key=lambda x: len(x[1]), reverse=True)
    for company, jobs in sorted_companies[:5]:
        output.append(f"• {company}: {len(jobs)}")
    
    # Recent Jobs (Limit to 10 to avoid Telegram message length limits)
    output.append("\n*🆕 LATEST 10 JOBS*")
    for i, job in enumerate(filtered_jobs[-10:], 1):
        output.append(f"{i}. {job['title']} @ {job['company']}")
        
    # Recommendations
    output.append("\n*💡 INSIGHTS*")
    remote_count = sum(1 for job in filtered_jobs if "remote" in job["location"].lower())
    if remote_count > len(filtered_jobs) * 0.5:
        output.append(f"• Remote market is hot ({remote_count} jobs)")
    else:
        output.append(f"• Mostly onsite roles ({len(filtered_jobs) - remote_count} jobs)")

    return "\n".join(output)

if __name__ == "__main__":
    print(analyze_job_history())