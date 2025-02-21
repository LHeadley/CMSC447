from pydantic import BaseModel


class ItemResponse(BaseModel):
    name: str
    unit_weight: int
    price: int
    stock: int


class MessageResponse(BaseModel):
    message: str


RESPONSE_404 = {404: {'model': MessageResponse, 'detail': 'Item not found.'}}
