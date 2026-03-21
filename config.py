"""
Configuration settings for the Job Hunter AU Bot.

This module contains all configurable parameters for the job scraper:
- Search terms organized by job category
- Blacklist and required keyword filters
- Location-based filtering rules
- Telegram message templates

Target: Specific roles for BIT + MICT + nursing background that support PR goals in Australia.
"""

# =============================================================================
# JOB SEARCH SETTINGS
# =============================================================================

# Location for job searches (currently Australia-wide)
LOCATION = "Australia"

# Number of results to fetch per search term (keep low to avoid rate limiting)
RESULTS_PER_TERM = 25

# =============================================================================
# SEARCH TERMS BY JOB CATEGORY
# =============================================================================
# Organized into 7 categories relevant to PR pathways (ANZSCO codes)
SEARCH_TERMS = [
    # --------------------------------------------------------------------------
    # Category 1: ICT Support Technician / Service Desk Analyst
    # ANZSCO: 313199 - ICT Support Technicians nec
    # --------------------------------------------------------------------------
    "IT Support Officer",
    "Service Desk Analyst",
    "Helpdesk Support",
    "Desktop Support Technician",
    "ICT Support Technician",
    "IT Support Specialist",
    "Technical Support Officer",
    "First Level Support",
    
    # --------------------------------------------------------------------------
    # Category 2: Clinical Systems Support Officer / Health ICT Support
    # Leverages nursing + IT background for healthcare IT roles
    # --------------------------------------------------------------------------
    "Clinical Systems Support Officer",
    "Health ICT Support",
    "Clinical Applications Support",
    "Aged Care Systems Support Officer",
    "eHealth Support Officer",
    "Healthcare IT Support",
    "Medical IT Support",
    "Clinical Support Analyst",
    
    # --------------------------------------------------------------------------
    # Category 3: Junior Systems Administrator
    # ANZSCO: 262113 - Systems Administrator
    # --------------------------------------------------------------------------
    "Junior Systems Administrator",
    "ICT Systems & Network Officer",
    "Infrastructure Support Officer",
    "Systems Administrator",
    "Network Administrator",
    "IT Infrastructure Officer",
    
    # --------------------------------------------------------------------------
    # Category 4: Junior Business Analyst / Process Analyst
    # ANZSCO: 261111 - ICT Business Analyst
    # --------------------------------------------------------------------------
    "Junior Business Analyst",
    "Systems Analyst",
    "Business Process Analyst",
    "Business Analyst",
    "IT Business Analyst",
    "Process Analyst",
    
    # --------------------------------------------------------------------------
    # Category 5: Junior Data / Reporting Analyst
    # Data-focused roles for analytics career path
    # --------------------------------------------------------------------------
    "Junior Data Analyst",
    "Reporting Officer",
    "BI Assistant",
    "Data Analyst",
    "Business Intelligence Analyst",
    "Reporting Analyst",
    
    # --------------------------------------------------------------------------
    # Category 6: Junior Software / Web Developer
    # ANZSCO: 261312 - Developer Programmer, 261313 - Software Engineer
    # --------------------------------------------------------------------------
    "Junior Software Developer",
    "Junior Web Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Software Developer",
    "Web Developer",
    "Application Developer",
    
    # --------------------------------------------------------------------------
    # Category 7: QA Tester / Software Tester
    # ANZSCO: 261314 - Software Tester
    # --------------------------------------------------------------------------
    "QA Engineer",
    "Software Tester",
    "Test Analyst",
    "UAT Tester",
    "Quality Assurance Analyst",
    "QA Tester"
]

# =============================================================================
# BLACKLIST KEYWORDS - Jobs containing these will be EXCLUDED
# =============================================================================
# Jobs matching any of these keywords will be filtered out
BLACKLIST_KEYWORDS = [
    # --- Seniority Exclusions ---
    # Exclude senior/lead roles that require extensive experience
    "senior", "lead", "principal", "staff", "manager", "head of", "director", 
    "5+ years", "7+ years", "10+ years", "sr", "seniour", "experienced",
    
    # --- Citizenship / Security Clearance Exclusions ---
    # Exclude jobs requiring citizenship or security clearance
    "australian citizen", "citizenship required", "citizens only",
    "must be australian", "must be a citizen", "citizen of australia",
    "permanent resident", "pr or citizen", "security clearance", 
    "nv1", "baseline", "defence", "clearance required", "defence clearance",
    "citizenship", "citizenship needed", "citizenship essential",
    
    # --- Work Type Exclusions ---
    # Exclude contract/freelance roles (part-time contract also excluded)
    "contract", "contractor", "freelance", "part-time contract"
]

# =============================================================================
# REQUIRED KEYWORDS - Jobs must contain at least ONE of these
# =============================================================================
# Jobs must mention at least one of these technology keywords to be considered relevant
REQUIRED_KEYWORDS = [
    # --- Core IT Skills ---
    "ICT", "Information Technology", "Helpdesk", "Service Desk", "Technical Support", 
    "IT Support", "Desktop Support", "Systems Administration", "SysAdmin",
    
    # --- Technical Skills ---
    "Network", "Networking", "Database", "SQL", "Business Intelligence", 
    "Data Analysis", "Business Analysis",
    "Software Development", "Programming", "Web Development",
    "Software Testing", "QA", "Quality Assurance", "UAT",
    "Cybersecurity", "Cloud", "Azure", "AWS",
    "Microsoft", "Office 365", "Exchange", "SharePoint",
    "Linux", "Windows Server", "VMware", "Virtualization",
    "Agile", "Scrum", "Power BI", "Tableau"
]

# =============================================================================
# ROLE-SPECIFIC KEYWORDS - Additional keywords for specific job categories
# =============================================================================
# These can be used for more granular filtering of specific role types
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

# =============================================================================
# LOCATION FILTERING TERMS
# =============================================================================

# Terms indicating job is in Darwin/Northern Territory (flexible criteria)
DARWIN_LOCATION_TERMS = ["darwin", "nt", "northern territory"]

# Terms indicating remote work (accept anywhere in Australia)
REMOTE_TERMS = ["remote", "work from home", "wfh", "anywhere", "virtual", "100% remote", "telecommute", "hybrid"]

# =============================================================================
# PR-RELEVANT OCCUPATION CODES (ANZSCO)
# =============================================================================
# Australian and New Zealand Standard Classification of Occupations codes
# for roles that may be relevant for Permanent Residency pathways
PR_OCCUPATIONS = [
    "313199",  # ICT Support Technicians nec
    "261111",  # ICT Business Analyst
    "262113",  # Systems Administrator
    "261312",  # Developer Programmer
    "261313",  # Software Engineer
    "261314"   # Software Tester
]

# =============================================================================
# TELEGRAM MESSAGE TEMPLATE
# =============================================================================
# Template for formatting job alerts sent via Telegram
TELEGRAM_MSG_TEMPLATE = (
    "🐊 *{title}*\n"
    "🏢 {company}\n"
    "📍 {location}\n"
    "📅 {posted_date}\n"
    "🔗 [Apply Here]({job_url})"
)