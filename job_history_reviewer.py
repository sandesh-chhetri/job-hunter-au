#!/usr/bin/env python3
"""
Job History Reviewer - Analyzes job history and returns structured data
"""
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

HISTORY_FILE = "job_history.json"

def load_job_history():
    """Loads job history from the JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def get_jobs_in_range(days=14):
    """
    Retrieves jobs from the history within a specified date range.
    
    Args:
        days (int): The number of days to look back.
    
    Returns:
        list: A list of job dictionaries.
    """
    history = load_job_history()
    cutoff_date = datetime.now() - timedelta(days=days)
    
    recent_jobs = []
    for entry in history:
        if 'timestamp' in entry and 'job_key' in entry:
            try:
                job_time = datetime.fromisoformat(entry["timestamp"])
                if job_time >= cutoff_date:
                    job_details = entry['job_key'].split('|')
                    if len(job_details) == 3:
                        recent_jobs.append({
                            "title": job_details[0],
                            "company": job_details[1],
                            "location": job_details[2],
                            "timestamp": entry["timestamp"]
                        })
            except (ValueError, TypeError):
                continue # Skip jobs with invalid timestamps
            
    return recent_jobs

def get_job_stats(days=14):
    """
    Generates statistics about jobs found in the last `days`.
    
    Args:
        days (int): The number of days to analyze.
        
    Returns:
        dict: A dictionary containing job statistics.
    """
    jobs = get_jobs_in_range(days)
    
    stats = {
        "total_jobs": len(jobs),
        "unique_companies": len(set(job["company"] for job in jobs)),
        "unique_locations": len(set(job["location"] for job in jobs)),
        "top_companies": defaultdict(int),
        "top_locations": defaultdict(int),
        "remote_jobs": 0,
        "days": days
    }
    
    for job in jobs:
        stats["top_companies"][job["company"]] += 1
        stats["top_locations"][job["location"]] += 1
        if "remote" in job["location"].lower():
            stats["remote_jobs"] += 1
            
    # Sort top companies and locations
    stats["top_companies"] = sorted(stats["top_companies"].items(), key=lambda x: x[1], reverse=True)[:5]
    stats["top_locations"] = sorted(stats["top_locations"].items(), key=lambda x: x[1], reverse=True)[:5]
    
    return stats

def get_recent_jobs(days=7, limit=10):
    """
    Retrieves the most recent jobs.
    
    Args:
        days (int): The number of days to look back.
        limit (int): The maximum number of jobs to return.
        
    Returns:
        list: A list of the most recent job dictionaries.
    """
    jobs = get_jobs_in_range(days)
    jobs.sort(key=lambda x: x["timestamp"], reverse=True)
    return jobs[:limit]

def format_report(stats, recent_jobs):
    """
    Formats the job report for display.
    
    Args:
        stats (dict): Job statistics from get_job_stats.
        recent_jobs (list): A list of recent jobs.
        
    Returns:
        str: A formatted string for the report.
    """
    report = [
        f"📈 *Job Stats (Last {stats.get('days', 14)} Days)*",
        f"Total Found: {stats['total_jobs']}",
        f"Unique Companies: {stats['unique_companies']}\n",
        "*🏢 TOP COMPANIES*",
    ]
    
    for company, count in stats["top_companies"]:
        report.append(f"• {company}: {count}")
        
    report.append("\n*🆕 LATEST JOBS*")
    if recent_jobs:
        for i, job in enumerate(recent_jobs, 1):
            report.append(f"{i}. {job['title']} @ {job['company']}")
    else:
        report.append("No recent jobs found.")
        
    report.append(f"\n*💡 INSIGHTS*")
    if stats['total_jobs'] > 0 and stats['remote_jobs'] > stats['total_jobs'] * 0.5:
        report.append(f"• Remote market is hot ({stats['remote_jobs']} jobs)")
    elif stats['total_jobs'] > 0:
        report.append(f"• Mostly onsite roles ({stats['total_jobs'] - stats['remote_jobs']} jobs)")
    else:
        report.append("No job data to generate insights.")
        
    return "\n".join(report)

if __name__ == "__main__":
    # Demonstrate the new functions
    job_stats = get_job_stats()
    latest_jobs = get_recent_jobs()
    
    print("--- Job Stats ---")
    print(job_stats)
    
    print("\n--- Recent Jobs ---")
    for job in latest_jobs:
        print(job)
        
    print("\n--- Formatted Report ---")
    print(format_report(job_stats, latest_jobs))