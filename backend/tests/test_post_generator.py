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

def test_generate_post_with_no_head_commit():
    payload = {
        "repository": {
            "name": "cool-repo",
            "html_url": "https://github.com/user/cool-repo"
        }
    }
    post = generate_post_from_webhook(payload)
    assert "cool-repo" in post
    assert "Someone" in post  # default fallback name

def test_generate_post_with_minimal_payload():
    payload = {}
    post = generate_post_from_webhook(payload)
    assert isinstance(post, str)
    assert len(post) > 0

