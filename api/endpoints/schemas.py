from pydantic import BaseModel
from domain import UserRole

class RefreshToken(BaseModel):
    value: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    role: UserRole


class ProductUnitCreate(BaseModel):
    content: str


class ProductUnitResponse(BaseModel):
    id: int
    is_sold: bool
    content: str | None = None


class ProductCreate(BaseModel):
    title: str
    description: str
    price: int


class CartItemUpdate(BaseModel):
    product_id: int
    quantity: int
