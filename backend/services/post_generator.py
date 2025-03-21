# post_generator.py

def generate_post_from_webhook(payload):
    repo = payload["repository"]["name"]
    url = payload["repository"]["html_url"]
    commit = payload["head_commit"]
    message = commit["message"]
    author = commit["author"]["name"]

    post = (
        f"🚀 Update to **{repo}** by {author}:\n\n"
        f"> \"{message}\"\n\n"
        f"🔗 {url}\n\n"
        "#buildinpublic #GitHubToLinkedIn"
    )
    return post
