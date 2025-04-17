import os
import pytest
from backend.app import create_app

def set_env_variables(env_vars):
    for key, value in env_vars.items():
        os.environ[key] = value

def clear_env_variables(env_vars):
    for key in env_vars.keys():
        os.environ.pop(key, None)

@pytest.fixture
def app():
    return create_app()

def test_app_starts_with_dummy_env_vars(app):
    dummy_env_vars = {
        "FLASK_ENV": "testing",
        "LINKEDIN_ACCESS_TOKEN": "dummy_token",
        "GITHUB_WEBHOOK_SECRET": "dummy_secret"
    }
    set_env_variables(dummy_env_vars)
    try:
        with app.app_context():
            assert app is not None
    finally:
        clear_env_variables(dummy_env_vars)

def test_app_crashes_without_required_env_vars_in_production():
    dummy_env_vars = {
        "FLASK_ENV": "production",
        "LINKEDIN_ACCESS_TOKEN": "dummy_token",
        "GITHUB_WEBHOOK_SECRET": "dummy_secret"
    }
    set_env_variables(dummy_env_vars)
    try:
        os.environ.pop("LINKEDIN_ACCESS_TOKEN")  # Simulate missing variable
        with pytest.raises(SystemExit):
            create_app()
    finally:
        clear_env_variables(dummy_env_vars)

def test_app_starts_without_env_vars_in_non_production():
    dummy_env_vars = {
        "FLASK_ENV": "development"
    }
    set_env_variables(dummy_env_vars)
    try:
        app = create_app()
        with app.app_context():
            assert app is not None
    finally:
        clear_env_variables(dummy_env_vars)