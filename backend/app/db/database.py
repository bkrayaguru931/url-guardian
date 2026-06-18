from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Railway provides DATABASE_URL automatically
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./url_guardian.db')

# Fix Railway's postgres:// to postgresql://
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Handle Railway's DATABASE_PUBLIC_URL
if not DATABASE_URL or DATABASE_URL == 'sqlite:///./url_guardian.db':
    DATABASE_URL = os.getenv('DATABASE_PUBLIC_URL', DATABASE_URL)

print(f"Using database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'SQLite'}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")