# Job Hunter AU 🇦🇺

An automated IT job scraping and alerting system for Australia, designed to find jobs relevant for Permanent Residency (PR) pathways.

## 📋 Overview

This system automatically scrapes IT job listings from Indeed and Google Jobs across Australia, filters them based on relevance and eligibility criteria, and sends real-time alerts via Telegram. It's specifically designed for individuals with BIT/MICT backgrounds seeking PR-relevant IT roles in Australia.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Every 4 Hours)           │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      main.py (Scraper)                       │
│  • Searches Indeed & Google Jobs                             │
│  • Filters by keywords & location                            │
│  • Deduplicates against history                              │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    config.py (Configuration)                 │
│  • Search terms (7 job categories)                          │
│  • Blacklist keywords (senior/citizenship)                   │
│  • Required technology keywords                              │
│  • Location filters (Darwin, Remote)                         │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  job_history.json (Database)                 │
│  • Stores seen job URLs                                      │
│  • Prevents duplicate alerts                                 │
│  • Keeps last 1000 entries                                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Integration                      │
│  • Real-time job alerts                                      │
│  • Interactive bot with commands                             │
│  • Job statistics and reports                                │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
job-hunter-au/
├── main.py                      # Core scraper and alert system
├── config.py                    # Configuration and search parameters
├── telegram_bot.py              # Interactive Telegram bot
├── job_history_reviewer.py      # Job history analytics module
├── test_bot.py                  # Unit tests for bot commands
├── requirements.txt             # Python dependencies
├── job_history.json             # Job history database
├── README.md                    # Project documentation
└── .github/
    └── workflows/
        └── scrape.yml           # GitHub Actions automation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram Chat ID(s) for receiving alerts

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sandesh-chhetri/job-hunter-au.git
   cd job-hunter-au
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   # Windows (PowerShell)
   $env:TELEGRAM_TOKEN="your_bot_token_here"
   $env:CHAT_ID="your_chat_id_here"
   
   # Linux/Mac
   export TELEGRAM_TOKEN="your_bot_token_here"
   export CHAT_ID="your_chat_id_here"
   ```

4. **Run the scraper:**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_TOKEN` | Telegram bot token from BotFather | Yes |
| `CHAT_ID` | Comma-separated list of chat IDs to receive alerts | Yes |

### Search Configuration (config.py)

#### Job Categories

The system searches for jobs across 7 categories relevant to PR pathways:

1. **ICT Support Technician / Service Desk Analyst**
   - IT Support Officer, Service Desk Analyst, Helpdesk Support
   - Desktop Support Technician, Technical Support Officer

2. **Clinical Systems Support Officer / Health ICT Support**
   - Clinical Systems Support Officer, Health ICT Support
   - Clinical Applications Support, eHealth Support Officer

3. **Junior Systems Administrator**
   - Junior Systems Administrator, ICT Systems & Network Officer
   - Infrastructure Support Officer, Network Administrator

4. **Junior Business Analyst / Process Analyst**
   - Junior Business Analyst, Systems Analyst
   - Business Process Analyst, IT Business Analyst

5. **Junior Data / Reporting Analyst**
   - Junior Data Analyst, Reporting Officer
   - BI Assistant, Business Intelligence Analyst

6. **Junior Software / Web Developer**
   - Junior Software Developer, Junior Web Developer
   - Backend Developer, Full Stack Developer

7. **QA Tester / Software Tester**
   - QA Engineer, Software Tester, Test Analyst
   - UAT Tester, Quality Assurance Analyst

#### Filtering Logic

**Blacklist Keywords** (jobs containing these are excluded):
- Seniority: senior, lead, principal, staff, manager, head of, director
- Experience: 5+ years, 7+ years, 10+ years
- Citizenship: australian citizen, citizenship required, security clearance

**Required Keywords** (jobs must contain at least one):
- Core IT: ICT, Helpdesk, Service Desk, Technical Support
- Technical: Network, Database, SQL, Software Development
- Tools: Power BI, Tableau, Azure, AWS, Linux, VMware

#### Location-Based Filtering

| Location Type | Filter Logic |
|---------------|--------------|
| **Darwin/NT** | Accept all jobs (flexible criteria) |
| **Remote** | Accept remote jobs anywhere in Australia |
| **Part-time** | Accept part-time jobs outside Darwin |
| **Other** | Skip unless part-time mentioned |

## 🤖 Telegram Bot Commands

The interactive bot supports the following commands:

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and command list |
| `/report` | Comprehensive job history report (last 14 days) |
| `/stats` | Quick job statistics summary |
| `/recent` | View the 10 most recent jobs (last 7 days) |
| `/help` | Show help and available commands |

### Example Bot Interaction

```
You: /stats

Bot: 📊 Job Statistics (Last 14 Days)

📈 Overview
• Total Jobs: 45
• Unique Companies: 32
• Unique Locations: 18

🏢 Top Companies
• Macquarie Group: 8 jobs
• NT Government: 5 jobs
• Compass Group: 4 jobs

📍 Top Locations
• Darwin: 12 jobs
• Remote: 8 jobs
• Sydney: 6 jobs
```

## 🔄 Automation

### GitHub Actions Workflow

The scraper runs automatically via GitHub Actions:

- **Schedule**: Every 4 hours (`0 */4 * * *`)
- **Manual Trigger**: Can be triggered manually via workflow_dispatch
- **Actions**:
  1. Checks out code
  2. Sets up Python 3.10
  3. Installs dependencies
  4. Runs the scraper
  5. Commits and pushes job_history.json updates

### Setting Up GitHub Actions

1. Go to your repository settings
2. Navigate to Secrets and variables > Actions
3. Add the following secrets:
   - `TELEGRAM_TOKEN`: Your Telegram bot token
   - `CHAT_ID`: Comma-separated chat IDs

## 📊 Job History

The `job_history.json` file stores previously seen jobs to prevent duplicate alerts:

```json
[
  {
    "title": "Service Desk Analyst",
    "company": "Centorrino Technologies",
    "url": "https://au.indeed.com/viewjob?jk=...",
    "scraped_at": "2026-02-03T15:21:53.202058"
  }
]
```

- **Maximum entries**: 1000 (oldest entries are removed)
- **Purpose**: Prevents sending duplicate job alerts
- **Updates**: Automatically committed by GitHub Actions

## 🧪 Testing

Run the unit tests for the Telegram bot:

```bash
python -m unittest test_bot.py
```

Tests cover:
- `/start` command welcome message
- `/report` command report generation
- `/stats` command statistics display
- `/recent` command recent jobs retrieval
- `/help` command help message

## 📝 PR-Relevant Occupation Codes

The system targets jobs matching these ANZSCO occupation codes:

| Code | Occupation |
|------|------------|
| 313199 | ICT Support Technicians nec |
| 261111 | ICT Business Analyst |
| 262113 | Systems Administrator |
| 261312 | Developer Programmer |
| 261313 | Software Engineer |
| 261314 | Software Tester |

## 🔧 Customization

### Adding New Search Terms

Edit `config.py` to add new search terms:

```python
SEARCH_TERMS = [
    # Add your custom terms here
    "Your Custom Job Title",
    # ... existing terms
]
```

### Modifying Filters

Adjust blacklist and required keywords in `config.py`:

```python
# Exclude jobs with these keywords
BLACKLIST_KEYWORDS = [
    "senior", "lead", "principal",
    # Add more...
]

# Jobs must contain at least one of these
REQUIRED_KEYWORDS = [
    "ICT", "Helpdesk", "Technical Support",
    # Add more...
]
```

### Changing Alert Frequency

Modify `.github/workflows/scrape.yml`:

```yaml
on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours (default)
    # - cron: '0 */2 * * *'  # Every 2 hours
    # - cron: '0 0 * * *'    # Daily at midnight
```

## 🛠️ Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| python-jobspy | >=1.1.18 | Job scraping from Indeed/Google |
| pandas | >=2.0.0 | Data manipulation and filtering |
| requests | >=2.31.0 | Telegram API communication |

## 📈 Statistics

The system has scraped **300+ jobs** since inception, with:
- Multiple job categories covered
- Real-time Telegram alerts
- Automatic deduplication
- Location-based filtering

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**Sandesh Chhetri**
- GitHub: [@sandesh-chhetri](https://github.com/sandesh-chhetri)

## 🙏 Acknowledgments

- [python-jobspy](https://github.com/cullenwatson/jobspy) for job scraping capabilities
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for Telegram integration
- GitHub Actions for automation

---

**Last Updated**: March 2026