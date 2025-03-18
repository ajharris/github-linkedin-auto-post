import json
import pytest
from backend.models import GitHubEvent
from backend.utils.security import generate_signature

def test_github_webhook(client, test_app):
    """Test handling of GitHub webhook push event."""
    
    # Mock payload for a push event
    mock_payload = {
        "repository": {"full_name": "testuser/testrepo"},
        "commits": [
            {
                "message": "Test commit",
                "author": {"name": "Test Author"},
                "url": "https://github.com/testuser/testrepo/commit/abcdef",
                "timestamp": "2025-03-18T12:34:56Z"
            }
        ]
    }

    # Convert mock payload to JSON bytes
    payload_bytes = json.dumps(mock_payload).encode()
    signature = generate_signature(payload_bytes)

    # Send the webhook request to the test client
    response = client.post(
        "/webhook/",
        data=payload_bytes,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": signature,  # GitHub signature header
        }
    )

    print("Raw Response Data:", response.data.decode("utf-8"))  # Debugging output

    # Check response status
    assert response.status_code == 200
    assert "status" in response.json
    assert response.json["status"] == "success"

    # ✅ Print database entries for debugging
    with test_app.app_context():
        all_events = GitHubEvent.query.all()
        print(f"Total events in database: {len(all_events)}")
        for e in all_events:
            print(f"Repo: {e.repo}, Message: {e.commit_message}, Author: {e.author}")

        event = GitHubEvent.query.filter_by(repo="testuser/testrepo").first()
        assert event is not None, "❌ No event was found in the database"
        assert event.commit_message == "Test commit"
        assert event.author == "Test Author"
        assert event.url == "https://github.com/testuser/testrepo/commit/abcdef"
