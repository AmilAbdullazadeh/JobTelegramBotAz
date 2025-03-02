import logging
from datetime import datetime
from sqlalchemy import func
from src.models import Job, Category, User, Keyword, get_session, init_db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles all database operations for the job bot"""
    
    def __init__(self):
        # Initialize the database if needed
        init_db()
    
    def add_jobs(self, jobs_data):
        """Add new jobs to the database, avoiding duplicates"""
        session = get_session()
        new_jobs_count = 0
        
        try:
            for job_data in jobs_data:
                # Check if job already exists by URL or external ID
                existing_job = None
                
                if job_data.get('url'):
                    existing_job = session.query(Job).filter(Job.url == job_data['url']).first()
                
                if not existing_job and job_data.get('external_id'):
                    existing_job = session.query(Job).filter(
                        Job.external_id == job_data['external_id'],
                        Job.source == job_data['source']
                    ).first()
                
                if existing_job:
                    # Update existing job if needed
                    continue
                
                # Get or create category
                category = None
                if job_data.get('category'):
                    category = session.query(Category).filter(
                        func.lower(Category.name) == func.lower(job_data['category'])
                    ).first()
                    
                    if not category:
                        category = Category(name=job_data['category'])
                        session.add(category)
                        session.flush()  # To get the category ID
                
                # Create new job
                new_job = Job(
                    title=job_data['title'],
                    company=job_data.get('company'),
                    location=job_data.get('location'),
                    description=job_data.get('description'),
                    url=job_data['url'],
                    source=job_data['source'],
                    external_id=job_data.get('external_id'),
                    posted_date=job_data.get('posted_date'),
                    category_id=category.id if category else None
                )
                
                session.add(new_job)
                new_jobs_count += 1
            
            session.commit()
            logger.info(f"Added {new_jobs_count} new jobs to the database")
            return new_jobs_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding jobs to database: {e}")
            return 0
        finally:
            session.close()
    
    def get_new_jobs_for_user(self, user_id, since_timestamp=None):
        """Get new jobs matching user's filters since the given timestamp"""
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found")
                return []
            
            # Base query for jobs
            query = session.query(Job)
            
            # Filter by timestamp if provided
            if since_timestamp:
                query = query.filter(Job.scraped_date >= since_timestamp)
            
            # Get user's category filters
            category_filters = [category.id for category in user.categories]
            
            # Get user's keyword filters
            keyword_filters = [keyword.word.lower() for keyword in user.keywords]
            
            # Apply filters if they exist
            if category_filters:
                query = query.filter(Job.category_id.in_(category_filters))
            
            # Get all jobs that match the category filter
            matching_jobs = query.all()
            
            # Further filter by keywords if needed
            if keyword_filters:
                filtered_jobs = []
                for job in matching_jobs:
                    job_title_lower = job.title.lower() if job.title else ""
                    if any(keyword in job_title_lower for keyword in keyword_filters):
                        filtered_jobs.append(job)
                matching_jobs = filtered_jobs
            
            return matching_jobs
            
        except Exception as e:
            logger.error(f"Error getting new jobs for user {user_id}: {e}")
            return []
        finally:
            session.close()
    
    def register_user(self, telegram_id, username=None, first_name=None, last_name=None):
        """Register a new user or update existing user"""
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            
            if user:
                # Update existing user
                if username:
                    user.username = username
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                
                logger.info(f"Updated user: {telegram_id}")
            else:
                # Create new user
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                logger.info(f"Registered new user: {telegram_id}")
            
            session.commit()
            return user.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error registering user {telegram_id}: {e}")
            return None
        finally:
            session.close()
    
    def add_category_filter(self, telegram_id, category_name):
        """Add a category filter for a user"""
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                logger.warning(f"User {telegram_id} not found")
                return False
            
            # Get or create category
            category = session.query(Category).filter(
                func.lower(Category.name) == func.lower(category_name)
            ).first()
            
            if not category:
                category = Category(name=category_name)
                session.add(category)
                session.flush()
            
            # Check if user already has this category
            if category in user.categories:
                logger.info(f"User {telegram_id} already has category filter: {category_name}")
                return False
            
            # Add category to user's filters
            user.categories.append(category)
            session.commit()
            logger.info(f"Added category filter '{category_name}' for user {telegram_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding category filter for user {telegram_id}: {e}")
            return False
        finally:
            session.close()
    
    def add_keyword_filter(self, telegram_id, keyword):
        """Add a keyword filter for a user"""
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                logger.warning(f"User {telegram_id} not found")
                return False
            
            # Get or create keyword
            keyword_obj = session.query(Keyword).filter(
                func.lower(Keyword.word) == func.lower(keyword)
            ).first()
            
            if not keyword_obj:
                keyword_obj = Keyword(word=keyword)
                session.add(keyword_obj)
                session.flush()
            
            # Check if user already has this keyword
            if keyword_obj in user.keywords:
                logger.info(f"User {telegram_id} already has keyword filter: {keyword}")
                return False
            
            # Add keyword to user's filters
            user.keywords.append(keyword_obj)
            session.commit()
            logger.info(f"Added keyword filter '{keyword}' for user {telegram_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding keyword filter for user {telegram_id}: {e}")
            return False
        finally:
            session.close()
    
    def get_user_filters(self, telegram_id):
        """Get all filters for a user"""
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                logger.warning(f"User {telegram_id} not found")
                return None
            
            return {
                'categories': [category.name for category in user.categories],
                'keywords': [keyword.word for keyword in user.keywords]
            }
            
        except Exception as e:
            logger.error(f"Error getting filters for user {telegram_id}: {e}")
            return None
        finally:
            session.close()
    
    def clear_user_filters(self, telegram_id):
        """Clear all filters for a user"""
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                logger.warning(f"User {telegram_id} not found")
                return False
            
            # Clear all filters
            user.categories = []
            user.keywords = []
            
            session.commit()
            logger.info(f"Cleared all filters for user {telegram_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error clearing filters for user {telegram_id}: {e}")
            return False
        finally:
            session.close()
    
    def remove_category_filter(self, telegram_id, category_name):
        """Remove a category filter for a user"""
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                logger.warning(f"User {telegram_id} not found")
                return False
            
            # Find the category
            category = session.query(Category).filter(
                func.lower(Category.name) == func.lower(category_name)
            ).first()
            
            if not category or category not in user.categories:
                logger.info(f"User {telegram_id} does not have category filter: {category_name}")
                return False
            
            # Remove category from user's filters
            user.categories.remove(category)
            session.commit()
            logger.info(f"Removed category filter '{category_name}' for user {telegram_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error removing category filter for user {telegram_id}: {e}")
            return False
        finally:
            session.close()
    
    def remove_keyword_filter(self, telegram_id, keyword):
        """Remove a keyword filter for a user"""
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                logger.warning(f"User {telegram_id} not found")
                return False
            
            # Find the keyword
            keyword_obj = session.query(Keyword).filter(
                func.lower(Keyword.word) == func.lower(keyword)
            ).first()
            
            if not keyword_obj or keyword_obj not in user.keywords:
                logger.info(f"User {telegram_id} does not have keyword filter: {keyword}")
                return False
            
            # Remove keyword from user's filters
            user.keywords.remove(keyword_obj)
            session.commit()
            logger.info(f"Removed keyword filter '{keyword}' for user {telegram_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error removing keyword filter for user {telegram_id}: {e}")
            return False
        finally:
            session.close()
    
    def set_user_active(self, telegram_id, is_active):
        """Set user's active status"""
        session = get_session()
        
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                logger.warning(f"User {telegram_id} not found")
                return False
            
            user.is_active = is_active
            session.commit()
            
            status = "active" if is_active else "inactive"
            logger.info(f"Set user {telegram_id} to {status}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error setting active status for user {telegram_id}: {e}")
            return False
        finally:
            session.close()
    
    def get_all_categories(self):
        """Get all available categories"""
        session = get_session()
        
        try:
            categories = session.query(Category).all()
            return [category.name for category in categories]
            
        except Exception as e:
            logger.error(f"Error getting all categories: {e}")
            return []
        finally:
            session.close()
    
    def get_active_users(self):
        """Get all active users"""
        session = get_session()
        
        try:
            users = session.query(User).filter(User.is_active == True).all()
            return users
            
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
        finally:
            session.close() 