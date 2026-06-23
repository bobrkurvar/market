import logging

from fastapi import APIRouter

from adapters.deps import UowDep
from api.schemas import HomePageOut, ProductWithStatsOut
from domain import Category, Product
from services.product import get_products_stats

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/home", response_model=HomePageOut)
async def get_home_page(uow: UowDep, limit: int = 8):
    async with uow:
        products = await uow.db.read(Product, limit=limit, loaded="variants")
        categories = await uow.db.read(Category, limit=limit, loaded="parent")
    stats = await get_products_stats(uow=uow, products=products)
    products_schemas = []
    for product in products:
        product_schema = ProductWithStatsOut(product=product, **stats.get(product.id, {}))
        products_schemas.append(product_schema)
    return {"products": products_schemas, "categories": categories}



