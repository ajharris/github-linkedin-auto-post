from flask import Blueprint
from routes.webhook import webhook_bp
from routes.provision import provision_bp
from auth import linkedin_oauth

def register_blueprints(app):
    """Register all Flask Blueprints."""
    app.register_blueprint(webhook_bp, url_prefix="/webhook")
    app.register_blueprint(provision_bp, url_prefix="/provision")

    if 'linkedin_oauth' in globals():
        app.register_blueprint(linkedin_oauth, url_prefix="/auth")
