import os
import logging
from urllib.parse import urlparse, urlunparse


def generate_post_from_webhook(payload):
    """
    Generate a simple LinkedIn post from a single GitHub webhook payload.

    Args:
        payload (dict): The GitHub webhook payload.

    Returns:
        str: A LinkedIn post.
    """
    linkedin_user_id = os.getenv("LINKEDIN_USER_ID", "someone")

    repo = payload.get("repository", {}).get("name", "a GitHub repo")
    url = payload.get("repository", {}).get("html_url", "https://github.com")
    commit = payload.get("head_commit", {})
    message = commit.get("message", "made an update")
    commit_author = commit.get("author", {}).get("name", "Someone")

    # Validate and fix URL scheme if necessary
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = urlunparse(parsed_url._replace(scheme="https"))

    author = f"urn:li:member:{linkedin_user_id}"

    # Ensure the URL is properly formatted before including it in the post
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError("Invalid URL format")

    return (
        f"{commit_author} just pushed to {repo}!\n\n"
        f"Commit message: \"{message}\"\n\n"
        f"Check it out: {url}\n\n"
        ""
    )


def generate_preview_post(data):
    """
    Generate a LinkedIn post preview from GitHub webhook payload.

    Args:
        data (dict): The GitHub webhook payload.

    Returns:
        str: A LinkedIn post preview.
    """
    commits = data.get("commits", [])
    repository = data.get("repository", {})
    repo_name = repository.get("name", "Unknown Repository")
    repo_url = repository.get("url", "#")

    if not commits:
        return "No commits to preview."

    if len(commits) == 1:
        commit = commits[0]
        message = commit.get("message", "No commit message")
        author = commit.get("author", {}).get("name", "Unknown Author")
        commit_url = commit.get("url", "#")

        return (
            f"{author} just pushed to {repo_name}!\n\n"
            f"Commit message: \"{message}\"\n\n"
            f"Check it out: {commit_url}\n\n"
        )

    # Digest-style preview for multiple commits
    preview = [f"Digest of updates in {repo_name}:"]
    for commit in commits[:5]:  # Limit to 5 commits for brevity
        message = commit.get("message", "No commit message")
        author = commit.get("author", {}).get("name", "Unknown Author")
        commit_url = commit.get("url", "#")
        preview.append(f"- {message} by {author} ({commit_url})")

    if len(commits) > 5:
        preview.append(f"...and {len(commits) - 5} more commits!\n")

    preview.append(f"Repository: {repo_url}\n\n")
    return "\n".join(preview)
