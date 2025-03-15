from backend.routes.webhook import webhook_bp
from backend.routes.provision import provision_bp
from backend.auth import linkedin_oauth

def register_blueprints(app):
    """Register all Flask Blueprints."""
    app.register_blueprint(webhook_bp, url_prefix="/webhook")
    app.register_blueprint(provision_bp, url_prefix="/provision")
    app.register_blueprint(linkedin_oauth, url_prefix="/auth")
