#!/usr/bin/env python3
"""
Interactive Telegram Bot for Job Hunter
Handles commands like /report, /stats, /help
"""
import asyncio
import logging
import os
import sys
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from job_history_reviewer import get_job_stats, get_recent_jobs, format_report

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    welcome_text = """
🤖 *Job Hunter Bot* 

I help you find Java jobs in Australia!

Available commands:
• `/report` - Get a comprehensive job history report
• `/stats` - Quick job statistics summary
• `/recent` - View the most recent jobs
• `/help` - Show this help message

I'll automatically send you new job opportunities every 3 hours!
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the comprehensive job history report."""
    try:
        stats = get_job_stats(days=14)
        recent_jobs = get_recent_jobs(days=14)
        report = format_report(stats, recent_jobs)
        
        await update.message.reply_text(report, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't generate the report.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send quick job statistics for the last 14 days."""
    try:
        stats = get_job_stats(days=14)
        
        stats_text = f"""
📊 *Job Statistics (Last 14 Days)*

📈 *Overview*
• Total Jobs: {stats['total_jobs']}
• Unique Companies: {stats['unique_companies']}
• Unique Locations: {stats['unique_locations']}

🏢 *Top Companies*
"""
        for company, count in stats["top_companies"]:
            stats_text += f"• {company}: {count} jobs\n"
        
        stats_text += "\n📍 *Top Locations*\n"
        for location, count in stats["top_locations"]:
            stats_text += f"• {location}: {count} jobs\n"
        
        if stats['remote_jobs'] > 0:
            stats_text += f"\n🌐 *Remote Jobs*: {stats['remote_jobs']}"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error generating stats: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't generate statistics.")

async def recent_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the most recent jobs from the last 7 days."""
    try:
        recent_jobs = get_recent_jobs(days=7, limit=10)
        
        if not recent_jobs:
            await update.message.reply_text("No recent jobs found in the last 7 days.")
            return
        
        jobs_text = f"🆕 *Latest {len(recent_jobs)} Jobs (Last 7 Days)*\n\n"
        for i, job in enumerate(recent_jobs, 1):
            job_time = datetime.fromisoformat(job['timestamp'])
            jobs_text += (
                f"{i}. *{job['title']}*\n"
                f"🏢 {job['company']}\n"
                f"📍 {job['location']}\n"
                f"🕐 {job_time.strftime('%Y-%m-%d %H:%M')}\n\n"
            )
        
        await update.message.reply_text(jobs_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting recent jobs: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't retrieve recent jobs.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message with all available commands."""
    help_text = """
📚 *Help & Commands* 

🔍 *Job Hunting Features*
• `/report` - Comprehensive job history report
• `/stats` - Quick overview of job statistics
• `/recent` - View most recent job postings

ℹ️ *Information*
• `/start` - Welcome message
• `/help` - This help message

🤖 *About*
I'm your Job Hunter Bot! I search for Java jobs in Australia and can provide detailed reports.
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main() -> None:
    """Start the Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_TOKEN environment variable not set.")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("recent", recent_command))
    application.add_handler(CommandHandler("help", help_command))
    
    logger.info("Starting Telegram bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
