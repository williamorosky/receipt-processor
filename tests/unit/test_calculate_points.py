import math
import pytest
from receipt_processor.models import Receipt, Item
from receipt_processor.services import calculate_points, ReceiptPointsCalculator


@pytest.mark.parametrize("receipt_data, expected_points", [
    (
            # Test Case 1: Minimal receipt with a round dollar total.
            {
                "retailer": "A",
                "purchaseDate": "2022-01-02",  # Even day; no odd-day bonus.
                "purchaseTime": "13:00",  # Not within bonus time window.
                "total": "1.00",  # Round dollar -> +50, also multiple of 0.25 -> +25.
                "items": [
                    {"shortDescription": "X", "price": "1.00"}  # No bonus since length 1 is not multiple of 3.
                ]
            },
            # Expected calculation:
            # Retailer: 1 point
            # Total round: 50 points
            # Multiple of 0.25: 25 points
            # Item pairs: 0 points (1 item)
            # Item bonus: 0 points
            # Date: 0 points (even day)
            # Time: 0 points (time not in bonus range)
            1 + 50 + 25
    ),
    (
            # Test Case 2: Two items where one item qualifies for description bonus, paired items, odd day, and time bonus.
            {
                "retailer": "AA",
                "purchaseDate": "2022-01-03",  # Odd day -> +6.
                "purchaseTime": "15:00",  # Within bonus window -> +10.
                "total": "2.25",  # Not round dollar, but multiple of 0.25 -> +25.
                "items": [
                    {"shortDescription": "abc", "price": "1.00"},  # len("abc") == 3 -> bonus = ceil(1.00*0.2)=1.
                    {"shortDescription": "defg", "price": "1.00"}  # No bonus (length 4 not multiple of 3).
                ]
            },
            # Expected calculation:
            # Retailer: 2 points
            # Total round: 0 points
            # Multiple of 0.25: 25 points
            # Item pairs: 1 pair -> 5 points
            # Item bonus: 1 point (for "abc")
            # Date: 6 points
            # Time: 10 points
            2 + 25 + 5 + 1 + 6 + 10
    ),
    (
            # Test Case 3: Multiple items, every pair counts and every item qualifies for bonus.
            {
                "retailer": "Retailer",
                "purchaseDate": "2022-02-05",  # Odd day -> +6.
                "purchaseTime": "10:00",  # Not in bonus time.
                "total": "5.75",  # Not round, but 5.75 is multiple of 0.25 -> +25.
                "items": [
                    {"shortDescription": "abc", "price": "1.00"},  # Bonus: ceil(0.2) = 1.
                    {"shortDescription": "abc", "price": "2.00"},  # Bonus: ceil(0.4) = 1.
                    {"shortDescription": "abcdef", "price": "3.00"},  # len("abcdef") = 6 -> bonus: ceil(0.6)=1.
                    {"shortDescription": "xyz", "price": "4.00"}  # Bonus: ceil(0.8)=1.
                ]
            },
            # Expected calculation:
            # Retailer: "Retailer" => 8 points
            # Total round: 0 points
            # Multiple of 0.25: 25 points
            # Item pairs: 4 items => 2 pairs => 2 * 5 = 10 points
            # Item bonus: 1 + 1 + 1 + 1 = 4 points
            # Date: 6 points
            # Time: 0 points
            8 + 25 + 10 + 4 + 6
    ),
    (
            # Test Case 4: Edge of the time bonus window (exactly 14:00) and even day.
            {
                "retailer": "Store",
                "purchaseDate": "2022-04-04",  # Even day -> 0 points.
                "purchaseTime": "14:00",  # Within bonus window -> +10.
                "total": "3.50",  # Not round, but multiple of 0.25 -> +25.
                "items": [
                    {"shortDescription": "aaa", "price": "1.00"},  # len("aaa") == 3 -> bonus: ceil(0.2)=1.
                    {"shortDescription": "bbb", "price": "2.00"}  # len("bbb") == 3 -> bonus: ceil(0.4)=1.
                ]
            },
            # Expected calculation:
            # Retailer: "Store" => 5 points
            # Total round: 0 points
            # Multiple of 0.25: 25 points
            # Item pairs: 1 pair => 5 points
            # Item bonus: 1 + 1 = 2 points
            # Date: 0 points
            # Time: 10 points
            5 + 25 + 5 + 2 + 10
    )
])
def test_calculate_points_modular(receipt_data, expected_points):
    receipt = Receipt(**receipt_data)
    # Using the modular calculator class
    calculator = ReceiptPointsCalculator(receipt)
    actual_points = calculator.calculate_points()
    assert actual_points == expected_points, f"Expected {expected_points}, got {actual_points}"
