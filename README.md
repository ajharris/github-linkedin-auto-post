### GitHub to LinkedIn Auto Poster
This project automates the creation and posting of LinkedIn updates based on GitHub activity. It uses a Flask backend to receive GitHub webhooks, generate post content, and publish to LinkedIn via the LinkedIn API. A React frontend allows for monitoring and potential manual post control.

## Features
GitHub Webhook Integration – Automatically listens for push events.

Auto-Generated LinkedIn Posts – Intelligent post creation based on commit data.

LinkedIn API Integration – Posts updates directly to your LinkedIn profile.

Robust Testing – Includes unit and integration tests for critical backend services.

Frontend UI – Built with React for future management and user controls.

## Project Structure
backend/ # Flask API backend and services
frontend/ # React frontend app
migrations/ # Database migration scripts
instance/ # SQLite development database
Procfile # For deployment on platforms like Heroku
requirements.txt # Backend dependencies

## Quick Start
Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
flask run

## Frontend
cd frontend
npm install
npm start

## Deployment
This app is configured for deployment on Heroku using a Procfile.

## Tests
Run backend tests with:

pytest backend/tests

## License
MIT License (or your preferred license)
