import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/jobbot.db")

# Job websites to scrape
JOB_WEBSITES = {
    "jobsearch": {
        "name": "JobSearch.az",
        "url": "https://jobsearch.az/vacancies",
        "base_url": "https://jobsearch.az"
    },
    "hellojob": {
        "name": "HelloJob.az",
        "url": "https://www.hellojob.az/is-elanlari/texnologiya",
        "base_url": "https://hellojob.az"
    },
    "smartjob": {
        "name": "SmartJob.az",
        "url": "https://smartjob.az/vacancies",
        "base_url": "https://smartjob.az"
    },
    "pashabank": {
        "name": "PashaBank Careers",
        "url": "https://careers.pashabank.az/az/page/vakansiyalar",
        "base_url": "https://careers.pashabank.az"
    },
    "kapitalbank": {
        "name": "KapitalBank HR",
        "url": "https://hr.kapitalbank.az/vacancy",
        "base_url": "https://hr.kapitalbank.az"
    },
    "busy": {
        "name": "Busy.az",
        "url": "https://busy.az/vacancies?categories%5B%5D=12&categories%5B%5D=81&categories%5B%5D=82&categories%5B%5D=83&categories%5B%5D=84&categories%5B%5D=85&categories%5B%5D=86&categories%5B%5D=87&categories%5B%5D=88&categories%5B%5D=90&categories%5B%5D=91&categories%5B%5D=92&categories%5B%5D=93&categories%5B%5D=154&fullSelect=on",
        "base_url": "https://busy.az"
    },
    "glorri": {
        "name": "Glorri Jobs",
        "url": "https://jobs.glorri.az/?jobFunctions=science-technology-engineering",
        "base_url": "https://jobs.glorri.az"
    }
}

# Scraping interval in minutes
SCRAPING_INTERVAL = int(os.getenv("SCRAPING_INTERVAL", "30"))

# Maximum number of pages to scrape per site
MAX_PAGES_PER_SITE = int(os.getenv("MAX_PAGES_PER_SITE", "3")) 