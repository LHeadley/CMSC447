from enum import Enum

from pydantic import BaseModel


# Item request for checkout/restock
class ItemRequest(BaseModel):
    name: str
    quantity: int


# Request for creating a new item
class CreateRequest(BaseModel):
    name: str
    unit_weight: int
    price: int
    initial_stock: int


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
