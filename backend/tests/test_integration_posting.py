import json
import pytest
from unittest.mock import patch
from backend.models import User, GitHubEvent, db
from backend.app import create_app

flask_app = create_app("testing")


GITHUB_PAYLOAD = {
    "repository": {
        "name": "awesome-repo",  # ← This line is essential
        "full_name": "user/awesome-repo",
        "html_url": "https://github.com/user/awesome-repo"
    },
    "head_commit": {
        "message": "Update README with new setup instructions",
        "url": "https://github.com/user/awesome-repo/commit/abc123",
        "author": {"name": "Dev User"}
    },
    "pusher": {
        "name": "testuser"
    }
}



@patch("backend.routes.verify_github_signature", return_value=True)
@patch("backend.routes.post_to_linkedin")
def test_github_event_creates_linkedin_post_and_saves_id(
    mock_post_to_linkedin, mock_verify, test_client
):
    # Arrange: Create user
    user = User(github_id="testuser", github_token="gh_token", linkedin_token="li_token")
    db.session.add(user)
    db.session.commit()

    # Mock LinkedIn API response
    mock_post_to_linkedin.return_value = {
        "status_code": 201,
        "id": "urn:li:ugcPost:987654321"
    }

    # Act: Simulate GitHub webhook
    res = test_client.post(
        "/webhook/github",
        data=json.dumps(GITHUB_PAYLOAD),
        content_type="application/json",
        headers={"X-GitHub-Event": "push", "X-Hub-Signature-256": "fake"}
    )

    # Assert
    assert res.status_code == 200
    event = GitHubEvent.query.first()
    assert event is not None
    assert event.repo_name == "user/awesome-repo"
    assert event.commit_message == "Update README with new setup instructions"
    assert event.commit_url == "https://github.com/user/awesome-repo/commit/abc123"
    assert event.linkedin_post_id == "urn:li:ugcPost:987654321"


@patch("backend.routes.verify_github_signature", return_value=True)
def test_webhook_fails_if_linkedin_credentials_missing(mock_verify, test_client):
    from backend.models import User, db
    user = User(github_id="testuser", github_token="gh_token", linkedin_token="li_token", linkedin_id=None)
    db.session.add(user)
    db.session.commit()

    payload = {
        "repository": {
            "name": "awesome-repo",
            "full_name": "user/awesome-repo",
            "html_url": "https://github.com/user/awesome-repo"
        },
        "head_commit": {
            "message": "Broken commit",
            "url": "https://github.com/user/awesome-repo/commit/def456",
            "author": {"name": "Dev User"}
        },
        "pusher": {
            "name": "testuser"
        }
    }

    res = test_client.post(
        "/webhook/github",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"X-GitHub-Event": "push", "X-Hub-Signature-256": "fake"}
    )

    assert res.status_code == 500
    assert b"Missing LinkedIn credentials" in res.data  # only if app returns error detail


def test_linkedin_author_format(client, requests_mock, app):
    # Arrange: create a test user with a bad LinkedIn ID (e.g. just digits)
    with app.app_context():
        user = User(
            github_id=7585359,
            github_token="fake_github_token",
            linkedin_token="fake_token",
            linkedin_id="AbCDefG123456789"  # ✅ fake but valid-length ID
        )        
        db.session.add(user)
        db.session.commit()

    # Intercept the LinkedIn API call
    linkedin_url = "https://api.linkedin.com/v2/ugcPosts"

    def request_callback(request, context):
        body = json.loads(request.body)
        author = body.get("author")
        assert author.startswith("urn:li:person:"), f"Invalid author format: {author}"
        assert len(author.split(":")[-1]) > 10, f"Author URN too short: {author}"
        context.status_code = 201  # LinkedIn returns 201 Created for successful posts
        return {"id": "urn:li:share:123456789"}


    import re
    requests_mock.post(re.compile(r"https://api\.linkedin\.com/v2/ugcPosts.*"), json=request_callback)


    # Act: simulate GitHub push event
    headers = {"X-GitHub-Event": "push"}
    data = {
        "repository": {"full_name": "ajharris/github-linkedin-auto-post"},
        "head_commit": {"message": "test commit"},
        "sender": {"id": 7585359}
    }
    response = client.post("/webhook/github", json=data, headers=headers)

    # Assert: still OK on our side, but test will fail if author is bad
    assert response.status_code == 200
    assert requests_mock.called, "LinkedIn mock was not called"

