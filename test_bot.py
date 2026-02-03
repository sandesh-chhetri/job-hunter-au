#!/usr/bin/env python3
"""
Test script for telegram bot functionality
"""
import asyncio
import unittest
import os
import sys
from unittest.mock import MagicMock, AsyncMock, patch

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import start, report_command, stats_command, recent_command, help_command

class TestBotCommands(unittest.TestCase):

    def setUp(self):
        """Set up a mock update and context for each test."""
        self.update = MagicMock()
        self.context = MagicMock()
        self.update.message = MagicMock()
        self.update.message.reply_text = AsyncMock()

    def test_start_command(self):
        """Test the /start command to ensure it returns the correct welcome message."""
        asyncio.run(start(self.update, self.context))
        self.update.message.reply_text.assert_called_once()
        call_args = self.update.message.reply_text.call_args
        self.assertIn("Job Hunter Bot", call_args[0][0])
        self.assertIn("/report", call_args[0][0])

    @patch('telegram_bot.get_job_stats')
    @patch('telegram_bot.get_recent_jobs')
    @patch('telegram_bot.format_report')
    def test_report_command(self, mock_format_report, mock_get_recent_jobs, mock_get_job_stats):
        """Test the /report command to ensure it returns a valid report."""
        # Mock the data-providing functions
        mock_get_job_stats.return_value = {"total_jobs": 1}
        mock_get_recent_jobs.return_value = [{"title": "Test Job"}]
        mock_format_report.return_value = "Job Stats Report"
        
        asyncio.run(report_command(self.update, self.context))
        
        self.update.message.reply_text.assert_called_once_with("Job Stats Report", parse_mode='Markdown')

    @patch('telegram_bot.get_job_stats')
    def test_stats_command(self, mock_get_job_stats):
        """Test the /stats command to ensure it returns job statistics."""
        mock_get_job_stats.return_value = {
            "total_jobs": 5,
            "unique_companies": 3,
            "unique_locations": 4,
            "top_companies": [("Company A", 2), ("Company B", 1)],
            "top_locations": [("Location X", 3), ("Location Y", 1)],
            "remote_jobs": 2,
        }
        
        asyncio.run(stats_command(self.update, self.context))
        
        self.update.message.reply_text.assert_called_once()
        call_args = self.update.message.reply_text.call_args
        self.assertIn("Job Statistics", call_args[0][0])

    @patch('telegram_bot.get_recent_jobs')
    def test_recent_command(self, mock_get_recent_jobs):
        """Test the /recent command to ensure it returns recent jobs."""
        mock_get_recent_jobs.return_value = [{
            "title": "Recent Job", 
            "company": "Company C", 
            "location": "Location Z", 
            "timestamp": "2023-10-27T10:00:00"
        }]
        
        asyncio.run(recent_command(self.update, self.context))
        
        self.update.message.reply_text.assert_called_once()
        call_args = self.update.message.reply_text.call_args
        self.assertIn("Latest", call_args[0][0])

    def test_help_command(self):
        """Test the /help command to ensure it returns the correct help message."""
        asyncio.run(help_command(self.update, self.context))
        self.update.message.reply_text.assert_called_once()
        call_args = self.update.message.reply_text.call_args
        self.assertIn("Help & Commands", call_args[0][0])

if __name__ == '__main__':
    unittest.main()