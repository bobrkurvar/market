from pydantic import BaseModel

from .category import CategoryOut
from .product import ProductWithStatsOut


class HomePageOut(BaseModel):
    categories: list[CategoryOut]
    products: list[ProductWithStatsOut]
