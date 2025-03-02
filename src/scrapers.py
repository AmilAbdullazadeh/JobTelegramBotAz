import requests
from bs4 import BeautifulSoup
import datetime
import logging
from src.config import JOB_WEBSITES, MAX_PAGES_PER_SITE

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseScraper:
    """Base scraper class with common functionality"""
    
    def __init__(self, site_key):
        self.site_key = site_key
        self.site_config = JOB_WEBSITES.get(site_key)
        if not self.site_config:
            raise ValueError(f"Unknown site key: {site_key}")
        
        self.base_url = self.site_config["base_url"]
        self.main_url = self.site_config["url"]
        self.name = self.site_config["name"]
        
    def get_page(self, url):
        """Get HTML content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_jobs(self, html):
        """Parse job listings from HTML - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement parse_jobs method")
    
    def get_job_details(self, job_url):
        """Get detailed job information - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement get_job_details method")
    
    def scrape(self):
        """Main scraping method"""
        all_jobs = []
        
        for page in range(1, MAX_PAGES_PER_SITE + 1):
            page_url = f"{self.main_url}?page={page}" if page > 1 else self.main_url
            logger.info(f"Scraping {self.name} page {page}: {page_url}")
            
            html = self.get_page(page_url)
            if not html:
                logger.warning(f"Failed to get page {page} from {self.name}")
                break
            
            jobs = self.parse_jobs(html)
            if not jobs:
                logger.info(f"No jobs found on page {page} from {self.name}")
                break
            
            all_jobs.extend(jobs)
            
            # If we got fewer jobs than expected, we've reached the end
            if len(jobs) < 10:  # Assuming each page has at least 10 jobs
                break
        
        logger.info(f"Scraped {len(all_jobs)} jobs from {self.name}")
        return all_jobs


class JobSearchScraper(BaseScraper):
    """Scraper for JobSearch.az"""
    
    def __init__(self):
        super().__init__("jobsearch")
    
    def parse_jobs(self, html):
        soup = BeautifulSoup(html, 'lxml')
        job_listings = []
        
        # Find all job listings on the page
        job_elements = soup.select('.job-listing')
        
        for job_element in job_elements:
            try:
                # Extract job information
                title_element = job_element.select_one('.job-title a')
                if not title_element:
                    continue
                
                title = title_element.text.strip()
                job_url = title_element['href']
                if not job_url.startswith('http'):
                    job_url = f"{self.base_url}{job_url}"
                
                company_element = job_element.select_one('.company-name')
                company = company_element.text.strip() if company_element else None
                
                location_element = job_element.select_one('.location')
                location = location_element.text.strip() if location_element else None
                
                category_element = job_element.select_one('.category')
                category = category_element.text.strip() if category_element else None
                
                # Get job details if needed
                job_details = self.get_job_details(job_url)
                
                job_data = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'category': category,
                    'url': job_url,
                    'description': job_details.get('description') if job_details else None,
                    'posted_date': job_details.get('posted_date') if job_details else None,
                    'source': self.name,
                    'external_id': job_details.get('external_id') if job_details else None
                }
                
                job_listings.append(job_data)
                
            except Exception as e:
                logger.error(f"Error parsing job from {self.name}: {e}")
                continue
        
        return job_listings
    
    def get_job_details(self, job_url):
        html = self.get_page(job_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            description_element = soup.select_one('.job-description')
            description = description_element.text.strip() if description_element else None
            
            date_element = soup.select_one('.posted-date')
            posted_date_str = date_element.text.strip() if date_element else None
            posted_date = None
            
            if posted_date_str:
                try:
                    # Example format: "Posted on: 15 May 2023"
                    date_part = posted_date_str.replace("Posted on:", "").strip()
                    posted_date = datetime.datetime.strptime(date_part, "%d %B %Y")
                except ValueError:
                    logger.warning(f"Could not parse date: {posted_date_str}")
            
            # Try to find an external ID
            external_id = None
            job_id_element = soup.select_one('.job-id')
            if job_id_element:
                external_id = job_id_element.text.strip().replace("Job ID:", "").strip()
            
            return {
                'description': description,
                'posted_date': posted_date,
                'external_id': external_id
            }
            
        except Exception as e:
            logger.error(f"Error getting job details from {self.name}: {e}")
            return None


class HelloJobScraper(BaseScraper):
    """Scraper for HelloJob.az"""
    
    def __init__(self):
        super().__init__("hellojob")
    
    def parse_jobs(self, html):
        soup = BeautifulSoup(html, 'lxml')
        job_listings = []
        
        # Find all job listings on the page
        job_elements = soup.select('.vacancy-item')
        
        for job_element in job_elements:
            try:
                # Extract job information
                title_element = job_element.select_one('.vacancy-name')
                if not title_element:
                    continue
                
                title = title_element.text.strip()
                
                url_element = job_element.select_one('a')
                job_url = url_element['href'] if url_element else None
                if job_url and not job_url.startswith('http'):
                    job_url = f"{self.base_url}{job_url}"
                
                company_element = job_element.select_one('.company-name')
                company = company_element.text.strip() if company_element else None
                
                location_element = job_element.select_one('.location')
                location = location_element.text.strip() if location_element else None
                
                category_element = job_element.select_one('.category')
                category = category_element.text.strip() if category_element else None
                
                # Get job details if needed
                job_details = self.get_job_details(job_url) if job_url else None
                
                job_data = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'category': category,
                    'url': job_url,
                    'description': job_details.get('description') if job_details else None,
                    'posted_date': job_details.get('posted_date') if job_details else None,
                    'source': self.name,
                    'external_id': job_details.get('external_id') if job_details else None
                }
                
                job_listings.append(job_data)
                
            except Exception as e:
                logger.error(f"Error parsing job from {self.name}: {e}")
                continue
        
        return job_listings
    
    def get_job_details(self, job_url):
        html = self.get_page(job_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            description_element = soup.select_one('.vacancy-description')
            description = description_element.text.strip() if description_element else None
            
            date_element = soup.select_one('.posted-date')
            posted_date_str = date_element.text.strip() if date_element else None
            posted_date = None
            
            if posted_date_str:
                try:
                    # Example format: "Posted on: 15 May 2023"
                    date_part = posted_date_str.replace("Posted on:", "").strip()
                    posted_date = datetime.datetime.strptime(date_part, "%d %B %Y")
                except ValueError:
                    logger.warning(f"Could not parse date: {posted_date_str}")
            
            # Try to find an external ID
            external_id = None
            job_id_element = soup.select_one('.vacancy-id')
            if job_id_element:
                external_id = job_id_element.text.strip()
            
            return {
                'description': description,
                'posted_date': posted_date,
                'external_id': external_id
            }
            
        except Exception as e:
            logger.error(f"Error getting job details from {self.name}: {e}")
            return None


class SmartJobScraper(BaseScraper):
    """Scraper for SmartJob.az"""
    
    def __init__(self):
        super().__init__("smartjob")
    
    def parse_jobs(self, html):
        soup = BeautifulSoup(html, 'lxml')
        job_listings = []
        
        # Find all job listings on the page
        job_elements = soup.select('.job-card')
        
        for job_element in job_elements:
            try:
                # Extract job information
                title_element = job_element.select_one('.job-title')
                if not title_element:
                    continue
                
                title = title_element.text.strip()
                
                url_element = job_element.select_one('a.job-link')
                job_url = url_element['href'] if url_element else None
                if job_url and not job_url.startswith('http'):
                    job_url = f"{self.base_url}{job_url}"
                
                company_element = job_element.select_one('.company')
                company = company_element.text.strip() if company_element else None
                
                location_element = job_element.select_one('.location')
                location = location_element.text.strip() if location_element else None
                
                category_element = job_element.select_one('.category')
                category = category_element.text.strip() if category_element else None
                
                # Get job details if needed
                job_details = self.get_job_details(job_url) if job_url else None
                
                job_data = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'category': category,
                    'url': job_url,
                    'description': job_details.get('description') if job_details else None,
                    'posted_date': job_details.get('posted_date') if job_details else None,
                    'source': self.name,
                    'external_id': job_details.get('external_id') if job_details else None
                }
                
                job_listings.append(job_data)
                
            except Exception as e:
                logger.error(f"Error parsing job from {self.name}: {e}")
                continue
        
        return job_listings
    
    def get_job_details(self, job_url):
        html = self.get_page(job_url)
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            description_element = soup.select_one('.job-description')
            description = description_element.text.strip() if description_element else None
            
            date_element = soup.select_one('.date')
            posted_date_str = date_element.text.strip() if date_element else None
            posted_date = None
            
            if posted_date_str:
                try:
                    # Example format: "15 May 2023"
                    posted_date = datetime.datetime.strptime(posted_date_str, "%d %B %Y")
                except ValueError:
                    logger.warning(f"Could not parse date: {posted_date_str}")
            
            # Try to find an external ID
            external_id = None
            # Extract ID from URL if possible
            if job_url and '/job/' in job_url:
                external_id = job_url.split('/job/')[1].split('/')[0]
            
            return {
                'description': description,
                'posted_date': posted_date,
                'external_id': external_id
            }
            
        except Exception as e:
            logger.error(f"Error getting job details from {self.name}: {e}")
            return None


class PashaBankScraper(BaseScraper):
    """Scraper for PashaBank Careers"""
    
    def __init__(self):
        super().__init__("pashabank")
    
    def parse_jobs(self, html):
        soup = BeautifulSoup(html, 'lxml')
        job_listings = []
        
        # Find all job listings on the page
        job_elements = soup.select('.vacancy-item, .vacancy-block')
        
        for job_element in job_elements:
            try:
                # Extract job information
                title_element = job_element.select_one('.vacancy-title, .vacancy-name')
                if not title_element:
                    continue
                
                title = title_element.text.strip()
                
                url_element = job_element.select_one('a')
                job_url = url_element['href'] if url_element else None
                if job_url and not job_url.startswith('http'):
                    job_url = f"{self.base_url}{job_url}"
                
                company = "PASHA Bank"
                location = "Baku, Azerbaijan"
                category = "Banking"
                
                # Get job details if needed
                job_details = self.get_job_details(job_url) if job_url else None
                
                job_data = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'category': category,
                    'url': job_url,
                    'description': job_details.get('description') if job_details else None,
                    'posted_date': job_details.get('posted_date') if job_details else None,
                    'source': self.name,
                    'external_id': job_details.get('external_id') if job_details else None
                }
                
                job_listings.append(job_data)
                
            except Exception as e:
                logger.error(f"Error parsing job from {self.name}: {e}")
                continue
        
        return job_listings
    
    def get_job_details(self, job_url):
        html = self.get_page(job_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            description_element = soup.select_one('.vacancy-description, .job-details')
            description = description_element.text.strip() if description_element else None
            
            date_element = soup.select_one('.vacancy-date, .posted-date')
            posted_date_str = date_element.text.strip() if date_element else None
            posted_date = None
            
            if posted_date_str:
                try:
                    # Try to parse the date
                    posted_date = datetime.datetime.now()  # Fallback to current date
                except ValueError:
                    logger.warning(f"Could not parse date: {posted_date_str}")
            
            # Try to find an external ID
            external_id = None
            if job_url:
                # Extract ID from URL if possible
                import re
                id_match = re.search(r'\/(\d+)(?:\/|$)', job_url)
                if id_match:
                    external_id = id_match.group(1)
            
            return {
                'description': description,
                'posted_date': posted_date,
                'external_id': external_id
            }
            
        except Exception as e:
            logger.error(f"Error getting job details from {self.name}: {e}")
            return None


class KapitalBankScraper(BaseScraper):
    """Scraper for KapitalBank HR"""
    
    def __init__(self):
        super().__init__("kapitalbank")
    
    def parse_jobs(self, html):
        soup = BeautifulSoup(html, 'lxml')
        job_listings = []
        
        # Find all job listings on the page
        job_elements = soup.select('.vacancy-item, .job-card')
        
        for job_element in job_elements:
            try:
                # Extract job information
                title_element = job_element.select_one('.vacancy-title, .job-title')
                if not title_element:
                    continue
                
                title = title_element.text.strip()
                
                url_element = job_element.select_one('a')
                job_url = url_element['href'] if url_element else None
                if job_url and not job_url.startswith('http'):
                    job_url = f"{self.base_url}{job_url}"
                
                company = "Kapital Bank"
                location = "Baku, Azerbaijan"
                category = "Banking"
                
                # Get job details if needed
                job_details = self.get_job_details(job_url) if job_url else None
                
                job_data = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'category': category,
                    'url': job_url,
                    'description': job_details.get('description') if job_details else None,
                    'posted_date': job_details.get('posted_date') if job_details else None,
                    'source': self.name,
                    'external_id': job_details.get('external_id') if job_details else None
                }
                
                job_listings.append(job_data)
                
            except Exception as e:
                logger.error(f"Error parsing job from {self.name}: {e}")
                continue
        
        return job_listings
    
    def get_job_details(self, job_url):
        html = self.get_page(job_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            description_element = soup.select_one('.vacancy-description, .job-details')
            description = description_element.text.strip() if description_element else None
            
            date_element = soup.select_one('.vacancy-date, .posted-date')
            posted_date_str = date_element.text.strip() if date_element else None
            posted_date = None
            
            if posted_date_str:
                try:
                    # Try to parse the date
                    posted_date = datetime.datetime.now()  # Fallback to current date
                except ValueError:
                    logger.warning(f"Could not parse date: {posted_date_str}")
            
            # Try to find an external ID
            external_id = None
            if job_url:
                # Extract ID from URL if possible
                import re
                id_match = re.search(r'\/(\d+)(?:\/|$)', job_url)
                if id_match:
                    external_id = id_match.group(1)
            
            return {
                'description': description,
                'posted_date': posted_date,
                'external_id': external_id
            }
            
        except Exception as e:
            logger.error(f"Error getting job details from {self.name}: {e}")
            return None


class BusyScraper(BaseScraper):
    """Scraper for Busy.az"""
    
    def __init__(self):
        super().__init__("busy")
    
    def parse_jobs(self, html):
        soup = BeautifulSoup(html, 'lxml')
        job_listings = []
        
        # Find all job listings on the page
        job_elements = soup.select('.vacancy-item, .job-item')
        
        for job_element in job_elements:
            try:
                # Extract job information
                title_element = job_element.select_one('.vacancy-title, .job-title')
                if not title_element:
                    continue
                
                title = title_element.text.strip()
                
                url_element = job_element.select_one('a')
                job_url = url_element['href'] if url_element else None
                if job_url and not job_url.startswith('http'):
                    job_url = f"{self.base_url}{job_url}"
                
                company_element = job_element.select_one('.company-name, .employer')
                company = company_element.text.strip() if company_element else None
                
                location_element = job_element.select_one('.location, .job-location')
                location = location_element.text.strip() if location_element else "Azerbaijan"
                
                category_element = job_element.select_one('.category, .job-category')
                category = category_element.text.strip() if category_element else "IT"
                
                # Get job details if needed
                job_details = self.get_job_details(job_url) if job_url else None
                
                job_data = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'category': category,
                    'url': job_url,
                    'description': job_details.get('description') if job_details else None,
                    'posted_date': job_details.get('posted_date') if job_details else None,
                    'source': self.name,
                    'external_id': job_details.get('external_id') if job_details else None
                }
                
                job_listings.append(job_data)
                
            except Exception as e:
                logger.error(f"Error parsing job from {self.name}: {e}")
                continue
        
        return job_listings
    
    def get_job_details(self, job_url):
        html = self.get_page(job_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            description_element = soup.select_one('.vacancy-description, .job-description')
            description = description_element.text.strip() if description_element else None
            
            date_element = soup.select_one('.vacancy-date, .posted-date')
            posted_date_str = date_element.text.strip() if date_element else None
            posted_date = None
            
            if posted_date_str:
                try:
                    # Try to parse the date
                    posted_date = datetime.datetime.now()  # Fallback to current date
                except ValueError:
                    logger.warning(f"Could not parse date: {posted_date_str}")
            
            # Try to find an external ID
            external_id = None
            if job_url:
                # Extract ID from URL if possible
                import re
                id_match = re.search(r'\/(\d+)(?:\/|$)', job_url)
                if id_match:
                    external_id = id_match.group(1)
            
            return {
                'description': description,
                'posted_date': posted_date,
                'external_id': external_id
            }
            
        except Exception as e:
            logger.error(f"Error getting job details from {self.name}: {e}")
            return None


class GlorriScraper(BaseScraper):
    """Scraper for Glorri Jobs"""
    
    def __init__(self):
        super().__init__("glorri")
    
    def parse_jobs(self, html):
        soup = BeautifulSoup(html, 'lxml')
        job_listings = []
        
        # Find all job listings on the page
        job_elements = soup.select('.job-card, .job-listing')
        
        for job_element in job_elements:
            try:
                # Extract job information
                title_element = job_element.select_one('.job-title, .position-title')
                if not title_element:
                    continue
                
                title = title_element.text.strip()
                
                url_element = job_element.select_one('a')
                job_url = url_element['href'] if url_element else None
                if job_url and not job_url.startswith('http'):
                    job_url = f"{self.base_url}{job_url}"
                
                company_element = job_element.select_one('.company-name, .employer')
                company = company_element.text.strip() if company_element else None
                
                location_element = job_element.select_one('.location, .job-location')
                location = location_element.text.strip() if location_element else "Azerbaijan"
                
                category_element = job_element.select_one('.category, .job-category')
                category = category_element.text.strip() if category_element else "Technology"
                
                # Get job details if needed
                job_details = self.get_job_details(job_url) if job_url else None
                
                job_data = {
                    'title': title,
                    'company': company,
                    'location': location,
                    'category': category,
                    'url': job_url,
                    'description': job_details.get('description') if job_details else None,
                    'posted_date': job_details.get('posted_date') if job_details else None,
                    'source': self.name,
                    'external_id': job_details.get('external_id') if job_details else None
                }
                
                job_listings.append(job_data)
                
            except Exception as e:
                logger.error(f"Error parsing job from {self.name}: {e}")
                continue
        
        return job_listings
    
    def get_job_details(self, job_url):
        html = self.get_page(job_url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            description_element = soup.select_one('.job-description, .description')
            description = description_element.text.strip() if description_element else None
            
            date_element = soup.select_one('.posted-date, .date')
            posted_date_str = date_element.text.strip() if date_element else None
            posted_date = None
            
            if posted_date_str:
                try:
                    # Try to parse the date
                    posted_date = datetime.datetime.now()  # Fallback to current date
                except ValueError:
                    logger.warning(f"Could not parse date: {posted_date_str}")
            
            # Try to find an external ID
            external_id = None
            if job_url:
                # Extract ID from URL if possible
                import re
                id_match = re.search(r'\/(\d+)(?:\/|$)', job_url)
                if id_match:
                    external_id = id_match.group(1)
            
            return {
                'description': description,
                'posted_date': posted_date,
                'external_id': external_id
            }
            
        except Exception as e:
            logger.error(f"Error getting job details from {self.name}: {e}")
            return None


def get_all_jobs():
    """Scrape jobs from all configured websites"""
    all_jobs = []
    
    scrapers = [
        JobSearchScraper(),
        HelloJobScraper(),
        SmartJobScraper(),
        PashaBankScraper(),
        KapitalBankScraper(),
        BusyScraper(),
        GlorriScraper()
    ]
    
    for scraper in scrapers:
        try:
            logger.info(f"Starting scraper for {scraper.name}")
            jobs = scraper.scrape()
            all_jobs.extend(jobs)
        except Exception as e:
            logger.error(f"Error with scraper {scraper.name}: {e}")
    
    logger.info(f"Total jobs scraped: {len(all_jobs)}")
    return all_jobs 