from datetime import date, time

from pydantic import BaseModel, Field
from typing import List


class Item(BaseModel):
    shortDescription: str = Field(
        ...,
        pattern=r"^[\w\s\-]+$",
        description="The Short Product Description for the item.",
        examples=["Mountain Dew 12PK"]
    )
    price: str = Field(
        ...,
        pattern=r"^\d+\.\d{2}$",
        description="The total price paid for this item.",
        examples=["6.49"]
    )


class Receipt(BaseModel):
    retailer: str = Field(
        ...,
        pattern=r"^[\w\s\-\&]+$",
        description="The name of the retailer or store the receipt is from.",
        examples=["M&M Corner Market"]
    )
    purchaseDate: date = Field(
        ...,
        description="The date of the purchase printed on the receipt (Format: YYYY-MM-DD).",
        examples=["2022-01-01"]
    )
    purchaseTime: time = Field(
        ...,
        description="The time of the purchase printed on the receipt in 24-hour format (HH:MM).",
        examples=["13:01"]
    )
    items: List[Item] = Field(
        ...,
        min_length=1,
        description="List of items purchased. Must contain at least one item."
    )
    total: str = Field(
        ...,
        pattern=r"^\d+\.\d{2}$",
        description="The total amount paid on the receipt.",
        examples=["6.49"]
    )


class ProcessResponse(BaseModel):
    id: str = Field(
        ...,
        pattern=r"^\S+$",
        description="Unique identifier for the processed receipt.",
        examples=["adb6b560-0eef-42bc-9d16-df48f30e89b2"]
    )


class PointsResponse(BaseModel):
    points: int = Field(
        ...,
        description="The number of points awarded for the receipt.",
        examples=[100]
    )
