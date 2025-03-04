from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ItemResponse(BaseModel):
    """
    Model representing an item returned by the /item endpoint.
    """
    id: int
    name: str
    stock: int
    max_checkout: int


class TransactionItemResponse(BaseModel):
    """
    Model representing a single item transaction (name, quantity pair)
    """
    item_name: str
    item_quantity: int


class TransactionResponse(BaseModel):
    """
    Model representing a transaction involving multiple item transactions (name, quantity pairs)
    """
    transaction_id: int
    student_id: Optional[str]
    day_of_week: str
    action: str
    timestamp: datetime
    items: list[TransactionItemResponse]


class MessageResponse(BaseModel):
    """
    Model representing a message sent by the server
    """
    message: str


RESPONSE_404 = {404: {'model': MessageResponse, 'detail': 'Item not found.'}}
