from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    database_url = db.Column(db.String(500), unique=True, nullable=False)
