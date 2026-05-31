from fastapi import APIRouter

from adapters.deps import UowDep
from adapters.web import GetSellerDep

from api.schemas import ProductCreate, ProductSellerListOut

router = APIRouter(prefix="")


@router.post("/product")
async def create_product(seller: GetSellerDep, product: ProductCreate, uow: UowDep):
    product = product.to_domain(seller)
    async with uow:
        return await uow.db.create(product)


@router.get("/seller/products", response_model=list[ProductSellerListOut])
async def get_seller_products(seller: GetSellerDep, uow: UowDep):
    async with uow:
        return await uow.product.read_products_with_variants_and_items(seller_id=seller.id)



# @router.patch("/product/{product_id}")
# async def change_product(
#     product_id: int, updated_product, seller: GetSellerDep, uow: UowDep
# ):
#     updated_domain_product = Product(
#         **updated_product.dump_model(), product_id=product_id
#     )
#     async with uow:
#         await uow.db.save(updated_domain_product)
