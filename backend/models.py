from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.String, unique=True, nullable=False)
    linkedin_id = db.Column(db.String, unique=True, nullable=True)
    github_token = db.Column(db.String, nullable=False)
    linkedin_token = db.Column(db.String, nullable=True)

class GitHubEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    repo_name = db.Column(db.String(255), nullable=False)
    commit_message = db.Column(db.Text, nullable=True)
    commit_url = db.Column(db.String(512), nullable=True)
    status = db.Column(db.String(50), default="pending")  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("github_events", lazy=True))

