#!/bin/bash

PROJECT_DIR=~/workspace/your-project  # Replace with your actual project folder name
ENV_FILE="$PROJECT_DIR/.env"

mkdir -p "$PROJECT_DIR"

echo "Creating sanitized .env file in $PROJECT_DIR using Codespaces secrets..."

cat <<EOF > "$ENV_FILE"
SQLALCHEMY_DATABASE_URI=$(echo -n "$SQLALCHEMY_DATABASE_URI" | tr -d '\n')
LINKEDIN_ACCESS_TOKEN=$(echo -n "$LINKEDIN_ACCESS_TOKEN" | tr -d '\n')
LINKEDIN_CLIENT_ID=$(echo -n "$LINKEDIN_CLIENT_ID" | tr -d '\n')
LINKEDIN_CLIENT_SECRET=$(echo -n "$LINKEDIN_CLIENT_SECRET" | tr -d '\n')
DATABASE_URL=$(echo -n "$DATABASE_URL" | tr -d '\n')
SECRET_GITHUB_TOKEN=$(echo -n "$SECRET_GITHUB_TOKEN" | tr -d '\n')
SECRET_GITHUB_SECRET=$(echo -n "$SECRET_GITHUB_SECRET" | tr -d '\n')
SEED_GITHUB_ID=$(echo -n "$SEED_GITHUB_ID" | tr -d '\n')
SEED_GITHUB_USERNAME=$(echo -n "$SEED_GITHUB_USERNAME" | tr -d '\n')
SEED_GITHUB_TOKEN=$(echo -n "$SEED_GITHUB_TOKEN" | tr -d '\n')
SEED_LINKEDIN_ID=$(echo -n "$SEED_LINKEDIN_ID" | tr -d '\n')
SEED_LINKEDIN_TOKEN=$(echo -n "$SEED_LINKEDIN_TOKEN" | tr -d '\n')
EOF

echo ".env file created successfully with sanitized values."
