from fastapi import APIRouter, UploadFile, File, Form, Depends

from adapters.deps import UowDep, HttpClientDep
from adapters.web import GetSellerDep
from adapters.images import ImageGenerator, ProductImagesManager
from services.product import create_product
from api.schemas import ProductCreate, ProductSellerListOut
from typing import Annotated

router = APIRouter()

def parse_product_json(
    data: Annotated[str, Form()]
) -> ProductCreate:
    return ProductCreate.model_validate_json(data)

@router.post("/product")
async def seller_create_product(
    seller: GetSellerDep,
    product_dto: Annotated[ProductCreate, Depends(parse_product_json)],
    file: Annotated[UploadFile, File()],
    uow: UowDep,
    http_client: HttpClientDep
):
    product = product_dto.to_domain(seller)
    img = await file.read()
    return await create_product(
        product=product,
        img=img,
        file_manager=ProductImagesManager(),
        img_generator=ImageGenerator(http_client),
        uow=uow
    )
    # product = product_dto.to_domain(seller)
    # async with uow:
    #     return await uow.db.create(product)


@router.get("/seller/products", response_model=list[ProductSellerListOut])
async def get_seller_products(seller: GetSellerDep, uow: UowDep):
    async with uow:
        return await uow.product.read_products_with_variants_and_items(seller_id=seller.id)


@router.get("/seller/categories")
async def get_catalog(uow: UowDep):
    async with uow:
        return await uow.category.get_leaf_categories()



