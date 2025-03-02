#!/usr/bin/env python3
"""
Initialize the database for the Job Posting Telegram Bot
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the current directory to the path so we can import the src package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import and run the database initialization
from src.init_database import main

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Initialize the database
    main()
    
    print("Database initialized successfully. You can now run the bot with: python3 run.py") 