import os
import logging
from urllib.parse import urlparse, urlunparse
from typing import List, Dict


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


def generate_digest_post(github_events, group_by_date=False, return_as_string=True):
    if not github_events:
        return "No events to summarize." if return_as_string else {}

    from collections import defaultdict

    grouped_commits = defaultdict(list)

    for event in github_events:
        repo_name = event.get("repository", {}).get("name", "Unknown Repository")
        commit_date = event.get("timestamp", "").split("T")[0] if group_by_date else None
        key = (repo_name, commit_date) if group_by_date else repo_name
        grouped_commits[key].append(event)

    summary = {}
    for key, events in grouped_commits.items():
        repo_name = key[0] if group_by_date else key
        date = key[1] if group_by_date else None
        messages = []
        tags = []
        # Ensure tags are added correctly
        for event in events:
            message = event.get("message") or event.get("head_commit", {}).get("message") or "No commit message"
            messages.append(message)
            if "fix" in message.lower():
                tags.append("#bugfix")
            if "refactor" in message.lower():
                tags.append("#refactor")
            if "test" in message.lower():
                tags.append("#testing")

        summary[key] = {
            "repo_name": repo_name,
            "date": date,
            "commits": events,
            "summary": "; ".join(messages),
            "tags": list(set(tags)),
        }

    # Ensure correct handling of return_as_string
    if return_as_string:
        lines = ["Here's a summary of recent GitHub activity:"]
        for key, data in summary.items():
            repo_line = f"- {data['repo_name']}"
            if group_by_date:
                repo_line += f" on {data['date']}"
            lines.append(repo_line)
            lines.append(f"  Summary: {data['summary']}")
            if data['tags']:
                lines.append(f"  Tags: {' '.join(data['tags'])}")
        return "\n".join(lines)

    return summary
