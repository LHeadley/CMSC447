from pydantic import BaseModel


# Item request for checkout/restock
class ActionRequest(BaseModel):
    name: str
    quantity: int


# Request for creating a new item
class CreateRequest(BaseModel):
    name: str
    unit_weight: int
    price: int
    initial_stock: int
