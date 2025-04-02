import json
import pytest
from unittest.mock import patch, Mock
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
    from backend.services.post_to_linkedin import post_to_linkedin  # ✅ real one
    from unittest.mock import patch

    # 👇 Disable autouse patch in this test
    with patch("backend.routes.post_to_linkedin", side_effect=post_to_linkedin):
        user = User(
            github_id="testuser",
            github_token="gh_token",
            linkedin_token="li_token",
            linkedin_id=None  # ❗ Missing on purpose
        )
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
            "pusher": {"name": "testuser"}
        }

        res = test_client.post(
            "/webhook/github",
            data=json.dumps(payload),
            content_type="application/json",
            headers={"X-GitHub-Event": "push", "X-Hub-Signature-256": "fake"}
        )

        assert res.status_code == 500
        assert b"Missing LinkedIn credentials" in res.data

@patch("backend.routes.verify_github_signature", return_value=True)
@patch("backend.routes.post_to_linkedin")
def test_linkedin_author_format(mock_post_to_linkedin, client, app):
    def fake_post_to_linkedin(user, repo_name, commit_message):
        print("✅ called post_to_linkedin with:", user.linkedin_id)
        assert user.linkedin_id.startswith("AbCDefG")
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "mocked"}
        return mock_response
    mock_post_to_linkedin.side_effect = fake_post_to_linkedin

    with app.app_context():
        user = User(
            github_id=7585359,
            github_token="fake_github_token",
            linkedin_token="fake_token",
            linkedin_id="AbCDefG123456789"
        )
        db.session.add(user)
        db.session.commit()

    headers = {"X-GitHub-Event": "push"}
    data = {
        "repository": {"full_name": "ajharris/github-linkedin-auto-post"},
        "head_commit": {"message": "test commit"},
        "sender": {"id": 7585359}
    }

    response = client.post("/webhook/github", json=data, headers=headers)
    assert response.status_code == 200, response.data
