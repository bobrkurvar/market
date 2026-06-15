import pytest
from services.product import create_product
from domain import Product, ProductVariant, ProductItem
from tests.fakes import FakeImgGenerator
from infra.security import async_hash_calculate
import logging

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_product(uow, saved_client, saved_seller, saved_category, product_images_manager):
    product = Product(
        title="title",
        seller=saved_seller,
        variants=ProductVariant(price=7, items=ProductItem(content="content")),
        category_id=saved_category.id,
        image_url="url",
        suggested_category="  GTA 5  "
    )
    created_product: Product = await create_product(
        uow=uow,
        product=product,
        img=b"a",
        file_manager=product_images_manager,
        img_generator=FakeImgGenerator(),
        hash_calculator=async_hash_calculate
    )

    assert created_product is not None
    assert created_product.image_url != "url"
    async with uow:
        db_product = await uow.db.read_one(Product, id=created_product.id, loaded="variants")
        db_variant = await uow.db.read_one(ProductVariant, product_id=created_product.id, loaded="items")
    assert (db_product.price, len(db_variant.items), db_product.suggested_category) == (7, 1, "gta5")