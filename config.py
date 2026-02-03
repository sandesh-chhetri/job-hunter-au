"""
Configuration settings for the Job Hunter Bot.
Targeting specific roles for BIT + MICT + nursing background that support PR goals.
"""

# Job Search Settings
LOCATION = "Australia"
RESULTS_PER_TERM = 15  # Keep low to avoid being blocked

# Search Terms: Focused on PR-relevant ICT roles
SEARCH_TERMS = [
    # Category 1: ICT Support Technician / Service Desk Analyst
    "IT Support Officer",
    "Service Desk Analyst",
    "Helpdesk Support",
    "Desktop Support Technician",
    "ICT Support Technician",
    "IT Support Specialist",
    "Technical Support Officer",
    "First Level Support",
    
    # Category 2: Clinical Systems Support Officer / Health ICT Support
    "Clinical Systems Support Officer",
    "Health ICT Support",
    "Clinical Applications Support",
    "Aged Care Systems Support Officer",
    "eHealth Support Officer",
    "Healthcare IT Support",
    "Medical IT Support",
    "Clinical Support Analyst",
    
    # Category 3: Junior Systems Administrator
    "Junior Systems Administrator",
    "ICT Systems & Network Officer",
    "Infrastructure Support Officer",
    "Systems Administrator",
    "Network Administrator",
    "IT Infrastructure Officer",
    
    # Category 4: Junior Business Analyst / Process Analyst
    "Junior Business Analyst",
    "Systems Analyst",
    "Business Process Analyst",
    "Business Analyst",
    "IT Business Analyst",
    "Process Analyst",
    
    # Category 5: Junior Data / Reporting Analyst
    "Junior Data Analyst",
    "Reporting Officer",
    "BI Assistant",
    "Data Analyst",
    "Business Intelligence Analyst",
    "Reporting Analyst",
    
    # Category 6: Junior Software / Web Developer
    "Junior Software Developer",
    "Junior Web Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Software Developer",
    "Web Developer",
    "Application Developer",
    
    # Category 7: QA Tester / Software Tester
    "QA Engineer",
    "Software Tester",
    "Test Analyst",
    "UAT Tester",
    "Quality Assurance Analyst",
    "QA Tester"
]

# Filters: Terms to EXCLUDE jobs
# Based on your preference to avoid "Senior" and "Citizenship" requirements
BLACKLIST_KEYWORDS = [
    # Seniority
    "senior", "lead", "principal", "staff", "manager", "head of", "director", 
    "5+ years", "7+ years", "10+ years", "sr", "seniour", "experienced",
    # Citizenship / Clearance
    "australian citizen", "citizenship required", "citizens only",
    "must be australian", "must be a citizen", "citizen of australia",
    "permanent resident", "pr or citizen", "security clearance", 
    "nv1", "baseline", "defence", "clearance required", "defence clearance",
    "citizenship", "citizenship needed", "citizenship essential",
    # Work Type Exclusions (only exclude full-time for non-Darwin jobs)
    "contract", "contractor", "freelance", "part-time contract"
]

# Technology Keywords: Jobs MUST mention at least one of these to be relevant
REQUIRED_KEYWORDS = [
    # Core IT Skills
    "IT", "ICT", "Information Technology", "Technology", "Systems",
    "Technical", "Support", "Helpdesk", "Service Desk",
    
    # Technical Skills
    "Network", "Networking", "System Administration", "Systems Admin",
    "Database", "SQL", "Data", "Reporting", "Business Intelligence",
    "Analysis", "Business Analysis", "Process Analysis",
    "Software", "Development", "Programming", "Web Development",
    "Testing", "QA", "Quality Assurance", "UAT",
    "Security", "Cybersecurity", "Cloud", "Azure", "AWS",
    "Microsoft", "Office", "365", "Exchange", "SharePoint",
    "Linux", "Windows", "VMware", "Virtualization",
    "Agile", "Scrum", "Project Management",
    "Power BI", "Tableau", "BI Tools", "Reporting Tools"
]

# Role-Specific Keywords (additional requirements for certain categories)
ROLE_SPECIFIC_KEYWORDS = {
    "Clinical": ["clinical", "health", "healthcare", "medical", "aged care", 
                "eHealth", "electronic health", "patient", "EMR", "EHR"],
    "Business Analyst": ["business", "process", "requirements", "stakeholders",
                        "user stories", "documentation", "analysis"],
    "Data Analyst": ["data", "analytics", "reporting", "BI", "Power BI",
                    "Tableau", "SQL", "data mining", "statistics"],
    "Developer": ["programming", "coding", "development", "application",
                 "web", "software", "API", "frontend", "backend"],
    "Systems Admin": ["server", "infrastructure", "administration", "AD",
                    "active directory", "backup", "monitoring", "VPN"]
}

# Darwin-specific settings
DARWIN_LOCATION_TERMS = ["darwin", "nt", "northern territory"]
REMOTE_TERMS = ["remote", "work from home", "wfh", "anywhere", "virtual", "100% remote", "telecommute", "hybrid"]

# PR-relevant occupation codes
PR_OCCUPATIONS = [
    "313199",  # ICT Support Technicians nec
    "261111",  # ICT Business Analyst
    "262113",  # Systems Administrator
    "261312",  # Developer Programmer
    "261313",  # Software Engineer
    "261314"   # Software Tester
]

# Alerting: Formatting for Telegram messages
TELEGRAM_MSG_TEMPLATE = (
    "🐊 *{title}*\n"
    "🏢 {company}\n"
    "📍 {location}\n"
    "📅 {posted_date}\n"
    "🔗 [Apply Here]({job_url})"
)