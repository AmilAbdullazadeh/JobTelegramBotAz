import asyncio
import logging
import schedule
import time
import threading
from datetime import datetime

from src.scrapers import get_all_jobs
from src.db_manager import DatabaseManager
from src.bot import get_bot
from src.config import SCRAPING_INTERVAL

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
db_manager = DatabaseManager()
bot = get_bot()
last_scrape_time = None

async def scrape_and_notify():
    """Scrape jobs and notify users about new ones"""
    global last_scrape_time
    
    current_time = datetime.utcnow()
    logger.info(f"Starting job scraping at {current_time}")
    
    # Scrape jobs from all websites
    jobs = get_all_jobs()
    
    # Add jobs to database
    new_jobs_count = db_manager.add_jobs(jobs)
    logger.info(f"Added {new_jobs_count} new jobs to database")
    
    # Notify users about new jobs
    if new_jobs_count > 0:
        await bot.notify_users_about_new_jobs(jobs, last_scrape_time)
    
    # Update last scrape time
    last_scrape_time = current_time
    logger.info(f"Job scraping completed at {datetime.utcnow()}")

def run_scraper():
    """Run the scraper in the event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scrape_and_notify())
    loop.close()

def schedule_scraper():
    """Schedule the scraper to run at regular intervals"""
    # Run immediately on startup
    threading.Thread(target=run_scraper).start()
    
    # Schedule to run every SCRAPING_INTERVAL minutes
    schedule.every(SCRAPING_INTERVAL).minutes.do(
        lambda: threading.Thread(target=run_scraper).start()
    )
    
    logger.info(f"Scheduled job scraping every {SCRAPING_INTERVAL} minutes")
    
    # Run the scheduler in a loop
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    """Main function to run the bot and scheduler"""
    logger.info("Starting Job Posting Bot")
    
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=schedule_scraper)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Run the bot
    bot.run()

if __name__ == "__main__":
    main() 