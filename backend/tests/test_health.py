def test_health_check(client):
    """Test if the health check endpoint is available."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}
