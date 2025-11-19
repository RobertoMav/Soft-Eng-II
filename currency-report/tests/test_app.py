from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_quote_usd_to_brl():
    response = client.get("/quote?from=USD&to=BRL")
    assert response.status_code == 200

    data = response.json()
    assert data["from"] == "USD"
    assert data["to"] == "BRL"
    assert "price" in data
    assert "timestamp" in data
    assert isinstance(data["price"], float)


def test_quote_with_different_currencies():
    response = client.get("/quote?from=EUR&to=BRL")
    assert response.status_code == 200

    data = response.json()
    assert data["from"] == "EUR"
    assert data["to"] == "BRL"
