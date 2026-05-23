from pydantic import BaseModel


class ProductUnitCreate(BaseModel):
    content: str  # Сам ключ или ссылка

class ProductUnitResponse(BaseModel):
    id: int
    is_sold: bool
    content: str | None = None # Скрываем, если не оплачено (логика в роуте)

class ProductCreate(BaseModel):
    title: str
    description: str
    price: int


class CartItemUpdate(BaseModel):
    product_id: int
    quantity: int