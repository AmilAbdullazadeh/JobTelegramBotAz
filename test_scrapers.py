#!/usr/bin/env python3
"""
Test the job scrapers
"""

import os
import sys
import logging
import json
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

# Import the scrapers
from src.scrapers import JobSearchScraper, HelloJobScraper, SmartJobScraper, PashaBankScraper, KapitalBankScraper, BusyScraper, GlorriScraper

def test_scraper(scraper_class, name):
    """Test a scraper and print the results"""
    print(f"\n\n{'=' * 50}")
    print(f"Testing {name} scraper")
    print(f"{'=' * 50}\n")
    
    try:
        scraper = scraper_class()
        jobs = scraper.scrape()
        
        print(f"Found {len(jobs)} jobs")
        
        if jobs:
            # Print the first job as an example
            print("\nExample job:")
            for key, value in jobs[0].items():
                print(f"{key}: {value}")
            
            # Save all jobs to a JSON file for inspection
            output_file = f"test_{scraper.site_key}_jobs.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\nAll jobs saved to {output_file}")
        
        return True
    except Exception as e:
        print(f"Error testing {name} scraper: {e}")
        return False

if __name__ == "__main__":
    print("Testing job scrapers...\n")
    
    scrapers = [
        (JobSearchScraper, "JobSearch.az"),
        (HelloJobScraper, "HelloJob.az"),
        (SmartJobScraper, "SmartJob.az"),
        (PashaBankScraper, "PashaBank.az"),
        (KapitalBankScraper, "KapitalBank.az"),
        (BusyScraper, "Busy.az"),
        (GlorriScraper, "Glorri.az")
    ]
    
    success_count = 0
    
    for scraper_class, name in scrapers:
        if test_scraper(scraper_class, name):
            success_count += 1
    
    print(f"\n\nTesting complete: {success_count}/{len(scrapers)} scrapers successful") 