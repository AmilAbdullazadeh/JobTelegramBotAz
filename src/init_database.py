import logging
from src.models import init_db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Initialize the database"""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

if __name__ == "__main__":
    main() 