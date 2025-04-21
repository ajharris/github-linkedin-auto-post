import requests
import os

# === CONFIG ===
REPO_OWNER = "ajharris"   # e.g. "gizmo"
REPO_NAME = "github-linkedin-auto-post"          # e.g. "github-to-linkedin"
SECRET_GITHUB_TOKEN = os.environ.get("SECRET_GITHUB_TOKEN")  # set this in your environment

BRANCH_TASKS = {
    "feature/env-variable-checks-for-production": "Check and fail gracefully if critical env vars are missing in production.",
    "feature/frontend-linkedin-post-preview": "Create a UI component to preview the LinkedIn post before sending.",
    "feature/frontend-ui-for-auth-status": "Improve the frontend to show GitHub and LinkedIn authentication status clearly.",
    "feature/generate-linkedin-post-content": "Implement rich LinkedIn post content generator from GitHub push data.",
    "feature/github-actions-ci-integration": "Set up GitHub Actions to run tests and fail on error or missing config.",
    "feature/github-oauth-login-flow": "Add GitHub OAuth login and callback flow with token storage.",
    "feature/github-webhook-integration-tests": "Write integration tests for GitHub webhook event handling.",
    "feature/linkedin-oauth-linking": "Add LinkedIn OAuth and link accounts to GitHub users.",
    "feature/remove-hardcoded-urls-for-deployment": "Replace hardcoded URLs in frontend/backend with env-based config.",
    "feature/send-post-to-linkedin-api": "Send generated post content to the LinkedIn API and log responses.",
    "feature/setup-env-example-sync-script": "Add a script to sync .env.example with required env variables.",
    "feature/webhook-handler-for-github-events": "Create webhook handler for GitHub events and trigger LinkedIn posts.",
    "frontendComponents": "Extract reusable frontend components like AuthStatus, PostPreview, LoginPanel.",
}

HEADERS = {
    "Authorization": f"Bearer {SECRET_GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

# === CREATE ISSUES ===
for branch, task in BRANCH_TASKS.items():
    title = f"[{branch}] {task.split('.')[0]}"
    body = f"### Task\n{task}\n\nBranch: `{branch}`"

    response = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues",
        headers=HEADERS,
        json={"title": title, "body": body}
    )

    if response.status_code == 201:
        issue = response.json()
        print(f"✅ Created issue: {issue['html_url']}")
    else:
        print(f"❌ Failed to create issue for {branch}: {response.text}")
