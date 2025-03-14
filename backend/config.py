import os

class Config:
    """Configuration settings for the Flask app."""
    
    DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///local.db")
    
    # Fix Heroku's `postgres://` issue for compatibility with SQLAlchemy
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
