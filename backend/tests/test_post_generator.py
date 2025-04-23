# tests/test_post_generator.py

import pytest
from backend.services.post_generator import generate_post_from_webhook


def test_generate_post_from_webhook():
    payload = {
        "repository": {
            "name": "awesome-project",
            "full_name": "user/awesome-project",
            "html_url": "https://github.com/yourusername/awesome-project",
        },
        "head_commit": {
            "message": "Add feature to auto-generate LinkedIn posts",
            "timestamp": "2025-03-21T12:00:00Z",
            "author": {"name": "Your Name"},
        },
    }

    post = generate_post_from_webhook(payload)
    assert "awesome-project" in post
    assert "Add feature to auto-generate LinkedIn posts" in post
    assert "Your Name" in post
    assert "#buildinpublic" in post
    assert "https://github.com/yourusername/awesome-project" in post


def test_generate_post_with_no_head_commit():
    payload = {
        "repository": {
            "name": "cool-repo",
            "full_name": "user/cool-repo",
            "html_url": "https://github.com/user/cool-repo",
        }
    }

    post = generate_post_from_webhook(payload)
    assert "cool-repo" in post
    assert "made an update" in post
    assert "Someone" in post  # default author fallback


def test_generate_post_with_minimal_payload():
    payload = {}

    post = generate_post_from_webhook(payload)
    assert isinstance(post, str)
    assert "a GitHub repo" in post
    assert "made an update" in post
    from urllib.parse import urlparse

    parsed_url = urlparse(post)
    assert "https://github.com" in post


def test_generate_post_with_partial_commit():
    payload = {
        "repository": {
            "name": "example-repo",
            "full_name": "example/example-repo",
            "html_url": "https://github.com/example/example-repo",
        },
        "head_commit": {
            "message": "Added support for LinkedIn posting",
            "author": {"name": "Alice"},
        },
    }

    post = generate_post_from_webhook(payload)
    assert "example-repo" in post
    assert "Added support for LinkedIn posting" in post
    assert "Alice" in post
    assert "https://github.com/example/example-repo" in post
    assert "#buildinpublic" in post


def test_generate_post_missing_author():
    payload = {
        "repository": {
            "name": "data-utils",
            "full_name": "org/data-utils",
            "html_url": "https://github.com/org/data-utils",
        },
        "head_commit": {"message": "Improve CSV export"},
    }

    post = generate_post_from_webhook(payload)
    assert "Someone" in post
    assert "Improve CSV export" in post
    assert "data-utils" in post


def test_generate_post_when_head_commit_is_missing():
    payload = {
        "repository": {
            "name": "my-repo",
            "full_name": "my-org/my-repo",
            "html_url": "https://github.com/my-org/my-repo",
        }
        # head_commit is omitted entirely
    }

    post = generate_post_from_webhook(payload)
    assert "my-repo" in post
    assert "made an update" in post
    assert "Someone" in post
