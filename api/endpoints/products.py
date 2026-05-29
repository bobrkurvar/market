from fastapi import APIRouter

from adapters.deps import UowDep
from domain import Product

router = APIRouter()


@router.get("/products")
async def get_catalog(uow: UowDep, limit: int, offset: int):
    async with uow:
        products = await uow.db.read(Product, limit=limit, offset=offset)
        count = await uow.db.count(Product)
    return {"items": products, "total": count}
