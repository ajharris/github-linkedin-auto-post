def test_auth_endpoint(client):
    """Test if the authentication route is reachable."""
    response = client.get("/auth/")  # Add trailing slash
    assert response.status_code in [200, 401]
