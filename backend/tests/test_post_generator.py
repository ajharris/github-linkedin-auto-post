# tests/test_post_generator.py

import pytest
from backend.services.post_generator import generate_preview_post


def test_generate_preview_post_single_commit():
    data = {
        "commits": [
            {
                "message": "Initial commit",
                "url": "https://github.com/example/repo/commit/abc123",
                "author": {"name": "John Doe"}
            }
        ],
        "repository": {"name": "example-repo", "url": "https://github.com/example/repo"}
    }
    result = generate_preview_post(data)
    assert "Initial commit" in result
    assert "John Doe" in result
    assert "https://github.com/example/repo/commit/abc123" in result
    assert "example-repo" in result


def test_generate_preview_post_multiple_commits():
    data = {
        "commits": [
            {
                "message": "Fix bug",
                "url": "https://github.com/example/repo/commit/def456",
                "author": {"name": "Jane Smith"}
            },
            {
                "message": "Add feature",
                "url": "https://github.com/example/repo/commit/ghi789",
                "author": {"name": "John Doe"}
            }
        ],
        "repository": {"name": "example-repo", "url": "https://github.com/example/repo"}
    }
    result = generate_preview_post(data)
    assert "Fix bug" in result
    assert "Add feature" in result
    assert "Jane Smith" in result
    assert "John Doe" in result
    assert "https://github.com/example/repo/commit/def456" in result
    assert "https://github.com/example/repo/commit/ghi789" in result
    assert "example-repo" in result


def test_generate_preview_post_digest():
    data = {
        "commits": [
            {
                "message": "Fix bug",
                "url": "https://github.com/example/repo1/commit/def456",
                "author": {"name": "Jane Smith"}
            },
            {
                "message": "Add feature",
                "url": "https://github.com/example/repo2/commit/ghi789",
                "author": {"name": "John Doe"}
            }
        ],
        "repository": {"name": "example-repo", "url": "https://github.com/example/repo"}
    }
    result = generate_preview_post(data)
    assert "Digest" in result
    assert "Fix bug" in result
    assert "Add feature" in result
    assert "Jane Smith" in result
    assert "John Doe" in result
    assert "https://github.com/example/repo1/commit/def456" in result
    assert "https://github.com/example/repo2/commit/ghi789" in result
