from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
from src.config import DATABASE_URL

Base = declarative_base()

# Association table for many-to-many relationship between users and categories
user_category = Table(
    'user_category', 
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

# Association table for many-to-many relationship between users and title keywords
user_keyword = Table(
    'user_keyword',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('keyword_id', Integer, ForeignKey('keywords.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    categories = relationship("Category", secondary=user_category, back_populates="users")
    keywords = relationship("Keyword", secondary=user_keyword, back_populates="users")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    
    # Relationships
    users = relationship("User", secondary=user_category, back_populates="categories")
    jobs = relationship("Job", back_populates="category")
    
    def __repr__(self):
        return f"<Category(name={self.name})>"

class Keyword(Base):
    __tablename__ = 'keywords'
    
    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True, nullable=False)
    
    # Relationships
    users = relationship("User", secondary=user_keyword, back_populates="keywords")
    
    def __repr__(self):
        return f"<Keyword(word={self.word})>"

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    url = Column(String, nullable=False)
    source = Column(String, nullable=False)  # Which website the job was scraped from
    external_id = Column(String, nullable=True)  # ID from the original website if available
    posted_date = Column(DateTime, nullable=True)
    scraped_date = Column(DateTime, default=datetime.datetime.utcnow)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="jobs")
    
    def __repr__(self):
        return f"<Job(title={self.title}, company={self.company}, source={self.source})>"

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new database session"""
    return Session() 