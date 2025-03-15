from backend.routes.webhook import webhook_bp
from backend.routes.provision import provision_bp
from backend.auth.linkedin_oauth import linkedin_oauth  # Make sure this is correct
from backend.routes.health import health_bp
from backend.routes.sample import sample_bp  # Ensure sample route exists

def register_blueprints(app):
    """Register all Flask Blueprints."""
    app.register_blueprint(webhook_bp, url_prefix="/webhook")
    app.register_blueprint(provision_bp, url_prefix="/provision")
    app.register_blueprint(linkedin_oauth, url_prefix="/auth")
    app.register_blueprint(health_bp, url_prefix="")  # Root path for health
    app.register_blueprint(sample_bp, url_prefix="")  # Root path for sample
