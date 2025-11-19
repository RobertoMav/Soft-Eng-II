from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


@patch("httpx.AsyncClient.get")
def test_history_usd_to_brl(mock_get):
    # Mock the response from currency-report service
    mock_response = MagicMock()
    mock_response.json = MagicMock(
        return_value={"from": "USD", "to": "BRL", "price": 5.42, "timestamp": "2025-11-19T10:30:00Z"}
    )
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    response = client.get("/history?from=USD&to=BRL")
    assert response.status_code == 200

    data = response.json()
    assert data["from"] == "USD"
    assert data["to"] == "BRL"
    assert "values" in data
    assert isinstance(data["values"], list)
    assert len(data["values"]) >= 1


@patch("httpx.AsyncClient.get")
def test_history_with_different_currencies(mock_get):
    # Mock the response from currency-report service
    mock_response = MagicMock()
    mock_response.json = MagicMock(
        return_value={"from": "EUR", "to": "BRL", "price": 5.89, "timestamp": "2025-11-19T10:30:00Z"}
    )
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    response = client.get("/history?from=EUR&to=BRL")
    assert response.status_code == 200

    data = response.json()
    assert data["from"] == "EUR"
    assert data["to"] == "BRL"
    assert len(data["values"]) >= 1


@patch("httpx.AsyncClient.get", side_effect=Exception("Service unavailable"))
def test_history_when_currency_report_fails(mock_get):
    response = client.get("/history?from=USD&to=BRL")
    assert response.status_code == 200

    data = response.json()
    assert data["from"] == "USD"
    assert data["to"] == "BRL"
    assert "values" in data
    assert len(data["values"]) >= 1
