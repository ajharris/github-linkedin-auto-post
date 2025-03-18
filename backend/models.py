from flask_sqlalchemy import SQLAlchemy
import os

from backend.extensions import db

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    database_url = db.Column(db.String(500), unique=True, nullable=False)

from datetime import datetime

class GitHubEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repo = db.Column(db.String(255), nullable=False)
    commit_message = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # ✅ Ensure DateTime type


