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


def generate_digest_post(commits, group_by_date=False):
    """
    Generate a digest post by grouping commits by repository and optionally by date.

    Args:
        commits (list): A list of commit dictionaries.
        group_by_date (bool): Whether to group commits by date.

    Returns:
        dict: A dictionary containing grouped and summarized commit data.
    """
    from collections import defaultdict
    from datetime import datetime

    grouped_commits = defaultdict(list)

    for commit in commits:
        repo_name = commit.get("repository", {}).get("name", "Unknown Repository")
        commit_date = commit.get("timestamp", "").split("T")[0] if group_by_date else None
        key = (repo_name, commit_date) if group_by_date else repo_name
        grouped_commits[key].append(commit)

    summary = {}
    for key, commits in grouped_commits.items():
        repo_name = key[0] if group_by_date else key
        date = key[1] if group_by_date else None
        messages = [commit.get("message", "") for commit in commits]
        tags = []
        for message in messages:
            if "fix" in message.lower():
                tags.append("#bugfix")
            if "refactor" in message.lower():
                tags.append("#refactor")
            if "test" in message.lower():
                tags.append("#testing")

        summary[key] = {
            "repo_name": repo_name,
            "date": date,
            "commits": commits,
            "summary": "; ".join(messages),
            "tags": list(set(tags)),
        }

    return summary
