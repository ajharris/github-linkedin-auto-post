# post_generator.py

from backend.services.post_to_linkedin import LINKEDIN_USER_ID


def generate_post_from_webhook(payload):
    repo = payload.get("repository", {}).get("name", "a GitHub repo")
    url = payload.get("repository", {}).get("html_url", "https://github.com")
    commit = payload.get("head_commit", {})
    message = commit.get("message", "made an update")
    author = f"urn:li:member:{LINKEDIN_USER_ID}"


    return (
        f"🚀 {author} just pushed to {repo}!\n\n"
        f"💬 Commit message: \"{message}\"\n\n"
        f"🔗 Check it out: {url}\n\n"
        "#buildinpublic #opensource"
    )

