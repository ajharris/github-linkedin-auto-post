# tests/test_post_generator.py

import pytest
from backend.services.post_generator import generate_preview_post, generate_digest_post


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


def test_generate_digest_post_group_by_repo():
    commits = [
        {"message": "Fix bug", "repository": {"name": "repo1"}, "timestamp": "2025-04-24T12:00:00Z"},
        {"message": "Add feature", "repository": {"name": "repo1"}, "timestamp": "2025-04-24T13:00:00Z"},
        {"message": "Refactor code", "repository": {"name": "repo2"}, "timestamp": "2025-04-24T14:00:00Z"},
    ]

    result = generate_digest_post(commits)

    assert "repo1" in result
    assert "repo2" in result
    assert len(result["repo1"]["commits"]) == 2
    assert len(result["repo2"]["commits"]) == 1
    assert "#bugfix" in result["repo1"]["tags"]
    assert "#refactor" in result["repo2"]["tags"]


def test_generate_digest_post_group_by_date():
    commits = [
        {"message": "Fix bug", "repository": {"name": "repo1"}, "timestamp": "2025-04-24T12:00:00Z"},
        {"message": "Add feature", "repository": {"name": "repo1"}, "timestamp": "2025-04-24T13:00:00Z"},
        {"message": "Refactor code", "repository": {"name": "repo1"}, "timestamp": "2025-04-23T14:00:00Z"},
    ]

    result = generate_digest_post(commits, group_by_date=True)

    assert ("repo1", "2025-04-24") in result
    assert ("repo1", "2025-04-23") in result
    assert len(result[("repo1", "2025-04-24")]["commits"]) == 2
    assert len(result[("repo1", "2025-04-23")]["commits"]) == 1


def test_generate_digest_post_tags():
    commits = [
        {"message": "Fix bug", "repository": {"name": "repo1"}},
        {"message": "Refactor code", "repository": {"name": "repo1"}},
        {"message": "Add tests", "repository": {"name": "repo1"}},
    ]

    result = generate_digest_post(commits)

    assert "#bugfix" in result["repo1"]["tags"]
    assert "#refactor" in result["repo1"]["tags"]
    assert "#testing" in result["repo1"]["tags"]
