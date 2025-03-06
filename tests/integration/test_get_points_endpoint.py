from fastapi.testclient import TestClient

from receipt_processor.main import app
from receipt_processor.models import Receipt
from receipt_processor.services import calculate_points

client = TestClient(app)


def test_get_points_valid_receipt():
    # First create a valid receipt via the POST endpoint.
    receipt_data = {
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
    }
    response_post = client.post("/receipts/process", json=receipt_data)
    assert response_post.status_code == 200
    receipt_id = response_post.json().get("id")
    assert receipt_id is not None

    # Retrieve points using the GET endpoint.
    response_get = client.get(f"/receipts/{receipt_id}/points")
    assert response_get.status_code == 200
    data = response_get.json()
    assert "points" in data

    # Verify that the calculated points match the business logic.
    receipt_obj = Receipt(**receipt_data)
    expected_points = calculate_points(receipt_obj)
    assert data["points"] == expected_points


def test_get_points_nonexistent_receipt():
    response = client.get("/receipts/nonexistent-id/points")
    assert response.status_code == 404
    # Ensure the error message matches the API specification.
    assert response.json()["detail"] == "No receipt found for that ID."
