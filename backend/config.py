import os



class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    
    # Load and fix DATABASE_URL for SQLAlchemy
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)  # Fix Heroku format
    else:
        raise ValueError("DATABASE_URL is not set! Make sure it's defined in your .env file or Heroku config.")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
