# GitHub LinkedIn Auto-Post

## Overview
This project automates the process of posting updates to LinkedIn based on GitHub activity. It integrates GitHub webhooks with LinkedIn's API to create posts whenever specific events occur in a GitHub repository, such as commits or pull requests.

## Features
- Automatically post GitHub activity to LinkedIn.
- Secure integration using environment variables and OAuth.
- CI/CD pipeline for automated testing and deployment.
- Modular and extensible codebase.

## Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- PostgreSQL database
- LinkedIn Developer Account for API credentials
- GitHub repository with webhook support

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/github-linkedin-auto-post.git
cd github-linkedin-auto-post
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root with the following variables:
```
SQLALCHEMY_DATABASE_URI=your_database_uri
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
DATABASE_URL=your_database_url
GITHUB_TOKEN=your_github_token
SECRET_GITHUB_SECRET=your_secret_github_secret
SEED_GITHUB_ID=your_seed_github_id
SEED_GITHUB_USERNAME=your_seed_github_username
SEED_GITHUB_TOKEN=your_seed_github_token
SEED_LINKEDIN_ID=your_seed_linkedin_id
SEED_LINKEDIN_TOKEN=your_seed_linkedin_token
LINKEDIN_USER_ID=your_linkedin_user_id
```

### 3. Install Dependencies
#### Backend
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

### 4. Run the Application
#### Backend
```bash
flask run
```

#### Frontend
```bash
cd frontend
npm start
```

## Testing
Run the test suite to ensure everything is working:
```bash
pytest
```

## Deployment
This project uses a `Procfile` for deployment to platforms like Heroku. Ensure all environment variables are set in the deployment environment.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.


