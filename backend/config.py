import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LINKEDIN_USER_ID = os.getenv("LINKEDIN_USER_ID")

    @staticmethod
    def init_app(app):
        pass  # For any app-specific initialization

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL", "sqlite:///dev.db")

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(BaseConfig):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL is not set! Make sure it's defined in your .env file or Heroku config.")
    SQLALCHEMY_DATABASE_URI = db_url.replace("postgres://", "postgresql://", 1)

# Dictionary to map config names to classes
config_dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,  # Set your default environment here
}
