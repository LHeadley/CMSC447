from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# Item request for checkout/restock
class ItemRequest(BaseModel):
    name: str
    quantity: int
    student_id: Optional[str] = Field(default=None)


class MultiItemRequest(BaseModel):
    student_id: Optional[str] = Field(default=None)
    items: list[ItemRequest]


# Request for creating a new item
class CreateRequest(BaseModel):
    name: str
    unit_weight: int
    price: int
    initial_stock: int
    supplier: Optional[str] = Field(default=None)


class WeekdayModel(str, Enum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'


class ActionTypeModel(str, Enum):
    CHECKOUT = 'checkout'
    RESTOCK = 'restock'
