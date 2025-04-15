# GitHub to LinkedIn Auto Poster

This project automates the creation and posting of LinkedIn updates based on GitHub activity. It uses a Flask backend to receive GitHub webhooks, generate post content, and publish to LinkedIn via the LinkedIn API. A React frontend allows for monitoring and potential manual post control.

## Features

- **GitHub Webhook Integration**: Automatically listens for push events.
- **Auto-Generated LinkedIn Posts**: Intelligent post creation based on commit data.
- **LinkedIn API Integration**: Posts updates directly to your LinkedIn profile.
- **Robust Testing**: Includes unit and integration tests for critical backend services.
- **Frontend UI**: Built with React for future management and user controls.

## Environment Variables

This app requires the following environment variables to be set in production. If any are missing, the app will fail fast to prevent misconfiguration.

### Required (for production)

- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `LINKEDIN_CLIENT_ID`
- `LINKEDIN_CLIENT_SECRET`
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_USER_ID`
- `SECRET_KEY`
- `DATABASE_URL`

### Optional (for development/testing)

In development or testing, these variables are optional. You can create a `.env` file to populate them locally:

#### Example `.env` file:
```
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_USER_ID=your_linkedin_user_id
SECRET_KEY=your_flask_secret_key
DATABASE_URL=postgresql://localhost/your_local_db
```

## Deployment

The app is hosted at:

[https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/](https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/)

> **Note**: The frontend is not yet complete.


