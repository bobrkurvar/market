from pydantic import BaseModel

# Схемы для Юнитов (ключей)
class ProductUnitCreate(BaseModel):
    content: str  # Сам ключ или ссылка

class ProductUnitResponse(BaseModel):
    id: int
    is_sold: bool
    content: str | None = None # Скрываем, если не оплачено (логика в роуте)

# Схемы для Товара (Витрины)
class ProductBase(BaseModel):
    title: str
    description: str
    price: int

class ProductCreate(ProductBase):
    salesperson_id: int

class ProductResponse(ProductBase):
    id: int
    salesperson_id: int
    # Кол-во считаем на лету или берем из поля
    available_quantity: int

# Схемы для Корзины
class CartItemUpdate(BaseModel):
    product_id: int
    quantity: int