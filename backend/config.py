import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Ensure DATABASE_URL uses the correct prefix
uri = os.getenv("DATABASE_URL", "").strip()
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
os.environ["DATABASE_URL"] = uri

REQUIRED_ENV_VARS = [
    "GITHUB_CLIENT_ID",
    "GITHUB_CLIENT_SECRET",
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
    LINKEDIN_USER_ID = os.getenv("LINKEDIN_USER_ID", os.getenv("SEED_LINKEDIN_ID", "default_user_id")).strip()
    GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "").strip()
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db").strip()
    DEBUG = False
    TESTING = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL", "sqlite:///dev.db").strip()

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db").strip()

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///prod.db").strip()

# Dictionary to map environment names to config classes
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
