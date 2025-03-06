import math
import logging
from datetime import datetime
from receipt_processor.models import Receipt

logger = logging.getLogger(__name__)


class ReceiptPointsCalculator:
    def __init__(self, receipt: Receipt):
        self.receipt = receipt

    def calculate_retailer_points(self) -> int:
        """1 point for every alphanumeric character in the retailer name."""
        retailer_points = sum(c.isalnum() for c in self.receipt.retailer)
        logger.debug("Retailer '%s' contributes %d points.", self.receipt.retailer, retailer_points)
        return retailer_points

    def calculate_total_round_dollar_points(self) -> int:
        """50 points if the total is a round dollar amount (no cents)."""
        try:
            total = float(self.receipt.total)
            logger.debug("Total parsed as: %.2f", total)
        except ValueError as e:
            logger.error("Error converting total '%s' to float: %s", self.receipt.total, e)
            return 0
        if total.is_integer():
            logger.debug("Added 50 points for round dollar total.")
            return 50
        return 0

    def calculate_total_multiple_of_quarter_points(self) -> int:
        """25 points if the total is a multiple of 0.25."""
        try:
            total = float(self.receipt.total)
        except ValueError as e:
            logger.error("Error converting total '%s' to float: %s", self.receipt.total, e)
            return 0
        if (total * 100) % 25 == 0:
            logger.debug("Added 25 points for total being a multiple of 0.25.")
            return 25
        return 0

    def calculate_item_pairs_points(self) -> int:
        """5 points for every two items on the receipt."""
        num_pairs = len(self.receipt.items) // 2
        bonus_points = num_pairs * 5
        logger.debug("Added %d points for %d item pairs.", bonus_points, num_pairs)
        return bonus_points

    def calculate_item_bonus_points(self) -> int:
        """
        For each item, if the trimmed description length is a multiple of 3,
        add the ceiling of (price * 0.2) to points.
        """
        bonus_points = 0
        for item in self.receipt.items:
            description = item.shortDescription.strip()
            if len(description) % 3 == 0:
                try:
                    item_price = float(item.price)
                    bonus = math.ceil(item_price * 0.2)
                    bonus_points += bonus
                    logger.debug(
                        "Item '%s' (price %s) qualifies for bonus: %d points.",
                        description, item.price, bonus
                    )
                except ValueError as e:
                    logger.error("Error converting item price '%s' to float: %s", item.price, e)
        return bonus_points

    def calculate_date_points(self) -> int:
        """6 points if the day in the purchase date is odd."""
        try:
            purchase_date = datetime.strptime(self.receipt.purchaseDate, "%Y-%m-%d")
            if purchase_date.day % 2 == 1:
                logger.debug("Added 6 points for odd purchase day (%d).", purchase_date.day)
                return 6
        except ValueError as e:
            logger.error("Error parsing purchaseDate '%s': %s", self.receipt.purchaseDate, e)
        return 0

    def calculate_time_points(self) -> int:
        """10 points if the purchase time is after 2:00pm and before 4:00pm."""
        try:
            purchase_time = datetime.strptime(self.receipt.purchaseTime, "%H:%M")
            if 14 <= purchase_time.hour < 16:
                logger.debug("Added 10 points for purchase time bonus (hour: %d).", purchase_time.hour)
                return 10
        except ValueError as e:
            logger.error("Error parsing purchaseTime '%s': %s", self.receipt.purchaseTime, e)
        return 0

    def calculate_points(self) -> int:
        """Compute the total points for the receipt by summing up all individual components."""
        logger.info("Starting points calculation for receipt from retailer: %s", self.receipt.retailer)
        total_points = (
                self.calculate_retailer_points() +
                self.calculate_total_round_dollar_points() +
                self.calculate_total_multiple_of_quarter_points() +
                self.calculate_item_pairs_points() +
                self.calculate_item_bonus_points() +
                self.calculate_date_points() +
                self.calculate_time_points()
        )
        logger.info("Completed points calculation: total points = %d", total_points)
        return total_points


def calculate_points(receipt: Receipt) -> int:
    """Helper function that instantiates the calculator and returns the calculated points."""
    calculator = ReceiptPointsCalculator(receipt)
    return calculator.calculate_points()
