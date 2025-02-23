from datetime import datetime
from typing import Union

from pydantic import BaseModel


class ItemResponse(BaseModel):
    name: str
    unit_weight: int
    price: int
    stock: int


class TransactionItemResponse(BaseModel):
    item_name: str
    item_quantity: int


class TransactionResponse(BaseModel):
    transaction_id: int
    student_id: Union[str, None]
    day_of_week: str
    action: str
    timestamp: datetime
    items: list[TransactionItemResponse]


class MessageResponse(BaseModel):
    message: str


RESPONSE_404 = {404: {'model': MessageResponse, 'detail': 'Item not found.'}}
