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
    }
}

# Scraping interval in minutes
SCRAPING_INTERVAL = 30

# Maximum number of pages to scrape per website
MAX_PAGES_PER_SITE = 3 