from fastapi import APIRouter, UploadFile, File, Form, Depends

from adapters.deps import UowDep, HttpClientDep, GetSellerDep, get_seller
from adapters.images import ImageGenerator, ProductImagesManager
from services.product import create_product
from api.schemas import ProductCreate, ProductSellerListOut
from infra.security import async_hash_calculate
from typing import Annotated
from domain import Category

router = APIRouter(prefix="/seller", dependencies=[Depends(get_seller)])

def parse_product_json(
    data: Annotated[str, Form()]
) -> ProductCreate:
    return ProductCreate.model_validate_json(data)

@router.post("/products")
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
        uow=uow,
        hash_calculator=async_hash_calculate
    )


@router.get("/products", response_model=list[ProductSellerListOut])
async def get_seller_products(seller: GetSellerDep, uow: UowDep):
    async with uow:
        return await uow.product.read_products_with_variants_and_items(seller_id=seller.id)


@router.get("/categories")
async def get_catalog(uow: UowDep):
    async with uow:
        #return await uow.category.get_leaf_categories()
        return await uow.db.read(Category, is_folder=True)



