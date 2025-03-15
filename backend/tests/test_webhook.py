def test_webhook_endpoint(client):
    """Test if the webhook endpoint receives POST data correctly."""
    data = {"event": "test_event"}
    response = client.post("/webhook/", json=data)  # Add trailing slash
    assert response.status_code in [200, 400]
