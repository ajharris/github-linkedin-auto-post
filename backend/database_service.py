import os
import psycopg2
from urllib.parse import urlparse
from flask_sqlalchemy import SQLAlchemy
from backend.models import db, Client

DATABASE_URL = os.getenv("DATABASE_URL")  # Get main database connection from Heroku

def create_client_database(client_name):
    """Creates a new database for a client and stores its connection."""
    
    # Parse the main database URL
    parsed_url = urlparse(DATABASE_URL)
    db_name = f"{client_name}_db"

    conn = psycopg2.connect(
        dbname="postgres",
        user=parsed_url.username,
        password=parsed_url.password,
        host=parsed_url.hostname,
        port=parsed_url.port
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Create the new client database
    cursor.execute(f"CREATE DATABASE {db_name}")
    conn.close()

    # Store the new database URL
    new_db_url = f"postgresql://{parsed_url.username}:{parsed_url.password}@{parsed_url.hostname}:{parsed_url.port}/{db_name}"
    
    client = Client(name=client_name, database_url=new_db_url)
    db.session.add(client)
    db.session.commit()

    return new_db_url
