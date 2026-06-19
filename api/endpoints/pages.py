import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from adapters.deps import UowDep
from api.schemas import HomePageOut, CategoryShortOut
from domain import Category, Product

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/home", response_model=HomePageOut)
async def get_home_page(uow: UowDep, limit: int = 8):
    async with uow:
        # categories = await uow.category.get_popular_categories_by_orders(6)
        # products = await uow.product.get_popular_products_by_orders(8)
        # categories, products = await asyncio.gather(*(categories_cor, products_cor))
        products = await uow.db.read(Product, limit=limit, loaded="variants")
        categories = await uow.db.read(Category, limit=limit, loaded="parent")
    return {"products": products, "categories": categories}



