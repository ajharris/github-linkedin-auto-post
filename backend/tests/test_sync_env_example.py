import os
import pytest
from backend.scripts.sync_env_example import sync_env_example

def setup_module(module):
    # Create temporary .env and .env.example files for testing
    with open('.env', 'w') as env:
        env.write("NEW_VAR=value\nEXISTING_VAR=value\n")

    with open('.env.example', 'w') as env_example:
        env_example.write("EXISTING_VAR=\nEXTRA_VAR=\n")

def teardown_module(module):
    # Clean up temporary files after tests
    os.remove('.env')
    os.remove('.env.example')

def test_sync_env_example_adds_missing_vars():
    sync_env_example()

    with open('.env.example', 'r') as env_example:
        content = env_example.read()

    assert "NEW_VAR=" in content
    assert "EXISTING_VAR=" in content

def test_sync_env_example_does_not_overwrite_values():
    sync_env_example()

    with open('.env.example', 'r') as env_example:
        content = env_example.read()

    assert "EXISTING_VAR=" in content
    assert "EXTRA_VAR=" in content

def test_sync_env_example_warns_about_extra_keys(capfd):
    sync_env_example()
    captured = capfd.readouterr()

    assert "Warning: .env.example contains extra keys not present in .env: EXTRA_VAR" in captured.out