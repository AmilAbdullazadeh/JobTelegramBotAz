#!/usr/bin/env python3
"""
Job Posting Telegram Bot
------------------------
A Telegram bot that monitors job postings from multiple Azerbaijani job websites.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the current directory to the path so we can import the src package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Check if the required environment variables are set
if not os.getenv("TELEGRAM_BOT_TOKEN"):
    print("Error: TELEGRAM_BOT_TOKEN environment variable is not set.")
    print("Please create a .env file based on .env.example and set your Telegram Bot Token.")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)

# Import and run the main function
from src.main import main

if __name__ == "__main__":
    main() 