import pytest
from unittest.mock import patch, MagicMock
from backend.services.post_to_linkedin import post_to_linkedin
from backend.models import User

@patch("backend.services.post_to_linkedin.requests.post")
@patch("backend.services.post_to_linkedin.generate_post_from_webhook")
def test_post_to_linkedin(mock_generate_post, mock_requests_post):
    mock_user = MagicMock()
    mock_user.linkedin_token = "test-token"
    mock_user.linkedin_id = "12345"
    mock_user.github_id = "test-github-id"

    webhook_payload = {
        "repository": {
            "name": "test-repo",
            "html_url": "https://github.com/test-repo"
        },
        "head_commit": {
            "message": "Initial commit",
            "author": {
                "name": "Test User"
            }
        }
    }

    mock_generate_post.return_value = "Generated post text"
    mock_requests_post.return_value.status_code = 201

    response = post_to_linkedin(mock_user, "test-repo", "Initial commit", webhook_payload)

    mock_generate_post.assert_called_once_with(webhook_payload)
    assert response.status_code == 201
