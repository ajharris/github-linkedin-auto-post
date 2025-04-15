import pytest
from backend.services.post_generator import generate_post_from_webhook

def test_generate_post_from_webhook():
    payload = {
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

    expected_text = (
        "🚀 Test User just pushed to test-repo!\n\n"
        "💬 Commit message: \"Initial commit\"\n\n"
        "🔗 Check it out: https://github.com/test-repo\n\n"
        "#buildinpublic #opensource"
    )

    result = generate_post_from_webhook(payload)
    assert result == expected_text
