from pydantic import BaseModel
from .category import CategoryOut
from .product import ProductOut

class HomePageOut(BaseModel):
    categories: list[CategoryOut]
    products: list[ProductOut]

