import os

DATABASE_URL = os.getenv("DATABASE_URL")  # From Heroku environment variables
SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgres://", "postgresql://", 1)  # Fix Heroku format
SQLALCHEMY_TRACK_MODIFICATIONS = False
