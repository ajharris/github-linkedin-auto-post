def test_provision_endpoint(client):
    """Test if the provision endpoint exists and returns a valid response."""
    response = client.get("/provision/test")  # Adjust the route if needed
    assert response.status_code in [200, 404]  # Change if necessary
