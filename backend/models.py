from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSON  # For JSON column support in PostgreSQL

db = SQLAlchemy()


class User(db.Model):
    """User model."""

    id = db.Column(db.Integer, primary_key=True)
    SECRET_GITHUB_id = db.Column(db.String(255), unique=True, nullable=False)
    SECRET_GITHUB_username = db.Column(db.String, nullable=True)
    SECRET_GITHUB_TOKEN = db.Column(db.String(255), nullable=False)
    linkedin_id = db.Column(db.String(255), unique=True, nullable=True)
    linkedin_token = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String, nullable=True)  # Optional: GitHub user's name
    email = db.Column(db.String, nullable=True)  # Optional: GitHub user's email
    avatar_url = db.Column(
        db.String, nullable=True
    )  # Optional: GitHub user's avatar URL
    extra_metadata = db.Column(
        JSON, nullable=True
    )  # Renamed from `metadata` to `extra_metadata`

    def has_valid_linkedin_token(self):
        """Check if the user has a valid LinkedIn token."""
        return self.linkedin_token is not None and self.linkedin_id is not None


class GitHubEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    repo_name = db.Column(db.String(255), nullable=False)
    commit_message = db.Column(db.Text, nullable=False)
    commit_url = db.Column(db.String(512), nullable=True)
    event_type = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), default="pending")
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    linkedin_post_id = db.Column(db.String(255), nullable=True)

    user = db.relationship("User", backref=db.backref("SECRET_GITHUB_events", lazy=True))
