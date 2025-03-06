import pytest
from fastapi.testclient import TestClient
from receipt_processor.main import app

client = TestClient(app)


@pytest.mark.parametrize("receipt_data", [
    # Valid example 1: Target receipt
    {
        "retailer": "Target",
        "purchaseDate": "2022-01-02",
        "purchaseTime": "13:13",
        "total": "35.35",
        "items": [
            {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
            {"shortDescription": "Emils Cheese Pizza", "price": "12.25"},
            {"shortDescription": "Knorr Creamy Chicken", "price": "1.26"},
            {"shortDescription": "Doritos Nacho Cheese", "price": "3.35"},
            {"shortDescription": "Klarbrunn 12-PK 12 FL OZ", "price": "12.00"},
        ]
    },
    # Valid example 2: M&M Corner Market receipt
    {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "total": "9.00",
        "items": [
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
        ]
    }
])
def test_process_valid_receipt(receipt_data):
    response = client.post("/receipts/process", json=receipt_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data


@pytest.mark.parametrize("invalid_payload", [
    # Missing required field: retailer.
    {
        "purchaseDate": "2022-01-02",
        "purchaseTime": "13:13",
        "total": "1.25",
        "items": [{"shortDescription": "Pepsi - 12-oz", "price": "1.25"}]
    },
    # Missing required field: purchaseDate.
    {
        "retailer": "Target",
        "purchaseTime": "13:13",
        "total": "1.25",
        "items": [{"shortDescription": "Pepsi - 12-oz", "price": "1.25"}]
    },
    # Invalid total format (should be two decimals).
    {
        "retailer": "Target",
        "purchaseDate": "2022-01-02",
        "purchaseTime": "13:13",
        "total": "1.2",
        "items": [{"shortDescription": "Pepsi - 12-oz", "price": "1.25"}]
    },
    # Invalid purchaseTime format.
    {
        "retailer": "Target",
        "purchaseDate": "2022-01-02",
        "purchaseTime": "13:130",
        "total": "1.25",
        "items": [{"shortDescription": "Pepsi - 12-oz", "price": "1.25"}]
    }
])
def test_process_invalid_receipt(invalid_payload):
    response = client.post("/receipts/process", json=invalid_payload)
    assert response.status_code == 400

    assert response.json()["detail"] == "The receipt is invalid."


def test_process_receipt_with_extra_fields():
    payload = {
        "retailer": "Target",
        "purchaseDate": "2022-01-02",
        "purchaseTime": "13:13",
        "total": "1.25",
        "items": [{"shortDescription": "Pepsi - 12-oz", "price": "1.25"}],
        "unexpected": "value"  # Extra field not defined in the model.
    }
    response = client.post("/receipts/process", json=payload)
    # Extra fields are ignored by default; thus, this request should succeed.
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
