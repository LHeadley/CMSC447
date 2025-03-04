from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ItemRequest(BaseModel):
    """
    Model representing a request to either checkout an item, or to restock an item.
    If this is used for restocking, student_id will be ignored by the server.
    If this is used for /checkout as a part of a larger MultiItemRequest, student_id will be ignored.
    student_id will only be used when using this model to check out a single item.
    """
    name: str
    quantity: int
    student_id: Optional[str] = Field(default=None)


class MultiItemRequest(BaseModel):
    """
    Model representing a request to checkout multiple items.
    student_id for each individual ItemRequest in items will be ignored in favor of this model's student_id.
    """
    student_id: Optional[str] = Field(default=None)
    items: list[ItemRequest]


class CreateRequest(BaseModel):
    """
    Model representing a request to create an item.
    """
    name: str
    initial_stock: int
    max_checkout: int

class WeekdayModel(str, Enum):
    """
    Enum model representing the days of the week when searching /logs by day of the week.
    """
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'


class ActionTypeModel(str, Enum):
    """
    Enum model representing the action type when searching /logs by action performed.
    """
    CHECKOUT = 'checkout'
    RESTOCK = 'restock'
