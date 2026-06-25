from pydantic import BaseModel
from datetime import datetime
from .base import BaseInput
from .product import ProductItemRead
from .review import ReviewRead


class OrderPaymentPayload(BaseModel):
    id: int


class OrderListRead(BaseModel):
    id: int
    status: str
    created_at: datetime
    product_snapshot: dict

    class Config:
        from_attributes = True

class OrderDetailRead(OrderListRead):
    items: list[ProductItemRead]
    review: ReviewRead | None = None


    class Config:
        from_attributes = True


class DisputeCreate(BaseInput):
    reason: str