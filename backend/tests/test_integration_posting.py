import json
import pytest
from unittest.mock import patch
from backend.models import User, GitHubEvent, db

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
