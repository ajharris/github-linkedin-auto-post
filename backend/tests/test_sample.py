def test_sample_endpoint(client):
    """Test the sample endpoint to ensure it returns a success message."""
    response = client.post("/sample/sample-endpoint", json={"key": "value"})
    assert response.status_code == 200
    assert "message" in response.json
    assert response.json["message"] == "Success"
    assert response.json["received"] == {"key": "value"}
