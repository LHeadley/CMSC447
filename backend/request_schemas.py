from pydantic import BaseModel


# Item request for checkout/restock
class ActionRequest(BaseModel):
    name: str
    quantity: int


# Request to get item data
class ItemRequest(BaseModel):
    name: str


# Request for creating a new item
class CreateRequest(BaseModel):
    name: str
    unit_weight: int
    price: int
    initial_stock: int
