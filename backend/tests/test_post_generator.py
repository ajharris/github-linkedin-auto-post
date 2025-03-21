# tests/test_post_generator.py

import pytest
from backend.services.post_generator import generate_post_from_webhook

sample_payload = {
    "repository": {
        "name": "awesome-project",
        "html_url": "https://github.com/yourusername/awesome-project"
    },
    "head_commit": {
        "message": "Add feature to auto-generate LinkedIn posts",
        "timestamp": "2025-03-21T12:00:00Z",
        "author": {
            "name": "Your Name"
        }
    }
}

def test_generate_post_from_webhook():
    post = generate_post_from_webhook(sample_payload)
    assert "awesome-project" in post
    assert "Add feature to auto-generate LinkedIn posts" in post
    assert "Your Name" in post
    assert "#buildinpublic" in post
    assert "https://github.com/yourusername/awesome-project" in post
