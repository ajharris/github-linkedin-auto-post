import pytest
from backend.services.post_generator import generate_digest_post

def test_generate_digest_post_group_by_repo():
    commits = [
        {"message": "Fix bug", "repository": {"name": "repo1"}, "timestamp": "2025-04-24T12:00:00Z"},
        {"message": "Add feature", "repository": {"name": "repo1"}, "timestamp": "2025-04-24T13:00:00Z"},
        {"message": "Refactor code", "repository": {"name": "repo2"}, "timestamp": "2025-04-24T14:00:00Z"},
    ]

    result = generate_digest_post(commits, return_as_string=False)

    assert "repo1" in result
    assert "repo2" in result
    assert len(result["repo1"]["commits"]) == 2


def test_generate_digest_post_group_by_date():
    commits = [
        {"message": "Fix bug", "repository": {"name": "repo1"}, "timestamp": "2025-04-24T12:00:00Z"},
        {"message": "Add feature", "repository": {"name": "repo1"}, "timestamp": "2025-04-24T13:00:00Z"},
        {"message": "Refactor code", "repository": {"name": "repo1"}, "timestamp": "2025-04-23T14:00:00Z"},
    ]

    result = generate_digest_post(commits, group_by_date=True, return_as_string=False)

    assert ("repo1", "2025-04-24") in result
    assert ("repo1", "2025-04-23") in result


def test_generate_digest_post_tags():
    commits = [
        {"message": "Fix bug", "repository": {"name": "repo1"}},
        {"message": "Refactor code", "repository": {"name": "repo1"}},
        {"message": "Add tests", "repository": {"name": "repo1"}},
    ]

    result = generate_digest_post(commits, return_as_string=False)

    tags = result["repo1"]["tags"]

    assert "#bugfix" in tags
    assert "#refactor" in tags
    assert "#testing" in tags


def test_generate_digest_post_multiple_events():
    events = [
        {
            "repository": {"name": "repo1"},
            "head_commit": {"message": "Fix bug", "author": {"name": "Alice"}}
        },
        {
            "repository": {"name": "repo2"},
            "head_commit": {"message": "Add feature", "author": {"name": "Bob"}}
        }
    ]

    result = generate_digest_post(events)

    assert "- repo1" in result
    assert "Summary: Fix bug" in result
    assert "- repo2" in result
    assert "Summary: Add feature" in result


def test_generate_digest_post_stress_test():
    events = [
        {
            "repository": {"name": f"repo{i}"},
            "head_commit": {"message": f"Commit {i}", "author": {"name": f"Author {i}"}}
        } for i in range(25)
    ]
    result = generate_digest_post(events)

    lines = result.splitlines()

    # The pattern is:
    # 1 header + (for each repo: 1 line for repo + 1 line for summary [+ 1 line for tags if any])
    repo_count = sum(1 for line in lines if line.startswith("- "))
    assert repo_count == 25

    assert lines[0].startswith("Here's a summary of recent GitHub activity:")

    for i in range(25):
        assert f"- repo{i}" in result
        assert f"Commit {i}" in result
