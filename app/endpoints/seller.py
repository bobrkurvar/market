from fastapi import APIRouter, HTTPException
from .schemas import ProductCreate
from adapters.deps import UowDep, GetSellerDep
from domain import Product

router = APIRouter()


@router.post("/product")
async def create_product(seller: GetSellerDep, product: ProductCreate, uow: UowDep):
    product = Product(**product.model_dump(), seller=seller)
    async with uow:
        await uow.db.create(product)





