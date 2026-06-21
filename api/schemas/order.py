from pydantic import BaseModel
from datetime import datetime


class OrderPaymentPayload(BaseModel):
    id: int

class ProductItemRead(BaseModel):
    id: int
    content: str


class OrderRead(BaseModel):
    id: int
    status: str
    created_at: datetime
    product_snapshot: dict
    items: list[ProductItemRead] = []

    class Config:
        from_attributes = True