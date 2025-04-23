import os
import logging


def generate_post_from_webhook(payload):
    try:
        linkedin_user_id = os.getenv("LINKEDIN_USER_ID", "someone")

        repo = payload.get("repository", {}).get("name", "a GitHub repo")
        url = payload.get("repository", {}).get("html_url", "https://github.com")
        commit = payload.get("head_commit", {})
        message = commit.get("message", "made an update")
        commit_author = commit.get("author", {}).get("name", "Someone")

        author = f"urn:li:member:{linkedin_user_id}"

        return (
            f"🚀 {commit_author} just pushed to {repo}!\n\n"
            f'💬 Commit message: "{message}"\n\n'
            f"🔗 Check it out: {url}\n\n"
            "#buildinpublic #opensource"
        )
    except Exception as e:
        logging.error(f"[Post Generator] Failed to generate post: {e}")
        raise
