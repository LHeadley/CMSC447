from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ItemResponse(BaseModel):
    name: str
    unit_weight: int
    price: int
    stock: int
    supplier: Optional[str]


class TransactionItemResponse(BaseModel):
    item_name: str
    item_quantity: int


class TransactionResponse(BaseModel):
    transaction_id: int
    student_id: Optional[str]
    day_of_week: str
    action: str
    timestamp: datetime
    items: list[TransactionItemResponse]


class MessageResponse(BaseModel):
    message: str


RESPONSE_404 = {404: {'model': MessageResponse, 'detail': 'Item not found.'}}
