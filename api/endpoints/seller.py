from fastapi import APIRouter, HTTPException

from adapters.deps import UowDep
from adapters.web import GetSellerDep
from domain import Product

from .schemas import ProductCreate

router = APIRouter(prefix="/seller")


@router.post("/product")
async def create_product(seller: GetSellerDep, product: ProductCreate, uow: UowDep):
    product = product.to_domain(seller)
    async with uow:
        return await uow.db.create(product)


@router.get("/products")
async def get_seller_products(seller: GetSellerDep, uow: UowDep):
    async with uow:
        return await uow.db.read(Product, seller_id=seller.id)


# @router.patch("/product/{product_id}")
# async def change_product(
#     product_id: int, updated_product, seller: GetSellerDep, uow: UowDep
# ):
#     updated_domain_product = Product(
#         **updated_product.dump_model(), product_id=product_id
#     )
#     async with uow:
#         await uow.db.save(updated_domain_product)
