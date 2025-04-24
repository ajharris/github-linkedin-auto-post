# Centralize dotenv loading
import os
from dotenv import load_dotenv
from backend.services.utils import get_database_url, get_linkedin_client_id, get_linkedin_client_secret

# Load environment variables once
load_dotenv()

# Use utility functions to set variables
LINKEDIN_CLIENT_ID = get_linkedin_client_id()
LINKEDIN_CLIENT_SECRET = get_linkedin_client_secret()
DATABASE_URL = get_database_url()
# Add other environment variables as needed

# Ensure DATABASE_URL uses the correct prefix
uri = get_database_url()

REQUIRED_ENV_VARS = [
    "SECRET_GITHUB_CLIENT_ID",
    "SECRET_GITHUB_CLIENT_SECRET",
    "LINKEDIN_CLIENT_ID",
    "LINKEDIN_CLIENT_SECRET",
    "LINKEDIN_ACCESS_TOKEN",
    "SEED_LINKEDIN_ID",  # Use SEED_LINKEDIN_ID instead of LINKEDIN_USER_ID
]


def get_required_env_var(key):
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value.strip()


# Load env vars conditionally based on environment
env = os.getenv("FLASK_ENV", "development").strip()

if env == "production":
    for key in REQUIRED_ENV_VARS:
        globals()[key] = get_required_env_var(key)
else:
    for key in REQUIRED_ENV_VARS:
        globals()[key] = os.getenv(key, "").strip()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret").strip()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LINKEDIN_USER_ID = os.getenv(
        "LINKEDIN_USER_ID", os.getenv("SEED_LINKEDIN_ID", "default_user_id")
    ).strip()
    SECRET_GITHUB_WEBHOOK_SECRET = os.getenv("SECRET_GITHUB_WEBHOOK_SECRET", "").strip()
    SQLALCHEMY_DATABASE_URI = get_database_url()
    DEBUG = False
    TESTING = False
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000").strip()


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL", "sqlite:///dev.db").strip()
    BACKEND_URL = os.getenv("DEV_BACKEND_URL", "http://dev.local").strip()


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db").strip()
    BACKEND_URL = os.getenv("TEST_BACKEND_URL", "http://test.local").strip()


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = get_database_url()
    DEBUG = False
    BACKEND_URL = os.getenv("PROD_BACKEND_URL", "https://prod.local").strip()


# Dictionary to map environment names to config classes
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
