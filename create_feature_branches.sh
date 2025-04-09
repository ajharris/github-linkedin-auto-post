#!/bin/bash

# Checkout dev branch and pull latest
git checkout dev && git pull

# List of feature branches to create
branches=(
  "feature/github-oauth-login-flow"
  "feature/linkedin-oauth-linking"
  "feature/webhook-handler-for-github-events"
  "feature/generate-linkedin-post-content"
  "feature/send-post-to-linkedin-api"
  "feature/github-webhook-integration-tests"
  "feature/env-variable-checks-for-production"
  "feature/github-actions-ci-integration"
  "feature/frontend-ui-for-auth-status"
  "feature/frontend-linkedin-post-preview"
  "feature/remove-hardcoded-urls-for-deployment"
  "feature/setup-env-example-sync-script"
)

# Create, checkout, and push each branch
for branch in "${branches[@]}"
do
  git checkout -b "$branch"
  git push -u origin "$branch"
done

# Return to dev branch at the end
git checkout dev

