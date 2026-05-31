from fastapi import APIRouter

from adapters.deps import UowDep
from domain import Product
from api.schemas import ProductCatalogListOut, ProductDetailOut

router = APIRouter()


@router.get("/products", response_model=ProductCatalogListOut)
async def get_catalog(uow: UowDep, limit: int, offset: int):
    async with uow:
        products = await uow.db.read(Product, loaded="variants", limit=limit, offset=offset)
        count = await uow.db.count(Product)
    return {"items": products, "total": count}


@router.get("/products/{product_id}", response_model=ProductDetailOut)
async def get_catalog(uow: UowDep, product_id: int):
    async with uow:
        return await uow.db.read_one(Product, id=product_id, loaded="variants", with_raise=True)

