import pytest
from flask import Flask
from backend.routes import github_webhook
from backend.config import GITHUB_WEBHOOK_SECRET
from unittest.mock import patch
import hmac
import hashlib
import json

def generate_signature(payload: str, secret: str):
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

@pytest.fixture
def client():
    app = Flask(__name__)
    app.testing = True
    app.add_url_rule('/webhook/github', view_func=github_webhook, methods=['POST'])
    with app.test_client() as client:
        yield client

@patch("backend.routes.current_app.logger")
def test_github_webhook_missing_payload(mock_logger, client):
    response = client.post('/webhook/github', data=None)
    assert response.status_code == 400
    mock_logger.error.assert_called_with("[Webhook] Missing payload in request.")

@patch("backend.routes.current_app.logger")
def test_github_webhook_invalid_signature(mock_logger, client):
    payload = json.dumps({"test": "data"})
    headers = {
        "X-Hub-Signature-256": "invalid_signature"
    }
    response = client.post('/webhook/github', data=payload, headers=headers)
    assert response.status_code == 400
    mock_logger.error.assert_called_with("[Webhook] Invalid signature.")

@patch("backend.routes.current_app.logger")
def test_github_webhook_unsupported_event(mock_logger, client):
    payload = json.dumps({"test": "data"})
    signature = generate_signature(payload, GITHUB_WEBHOOK_SECRET)
    headers = {
        "X-Hub-Signature-256": f"sha256={signature}",
        "X-GitHub-Event": "unsupported_event"
    }
    response = client.post('/webhook/github', data=payload, headers=headers)
    assert response.status_code == 400
    mock_logger.info.assert_called_with("[Webhook] Unsupported event type: unsupported_event")

@patch("backend.routes.current_app.logger")
def test_github_webhook_valid_event(mock_logger, client):
    payload = json.dumps({"test": "data"})
    signature = generate_signature(payload, GITHUB_WEBHOOK_SECRET)
    headers = {
        "X-Hub-Signature-256": f"sha256={signature}",
        "X-GitHub-Event": "push"
    }
    response = client.post('/webhook/github', data=payload, headers=headers)
    assert response.status_code == 200
    mock_logger.info.assert_any_call("[Webhook] Received event type: push")
    mock_logger.info.assert_any_call(f"[Webhook] Payload: {json.loads(payload)}")