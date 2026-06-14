import pytest
from services.product import create_product
from domain import Product, ProductVariant, ProductItem
from .fakes import FakeImgGenerator
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
        img_generator=FakeImgGenerator()
    )

    assert created_product is not None
    assert created_product.image_url != "url"
    async with uow:
        db_variant = await uow.db.read_one(ProductVariant, product_id=created_product.id, loaded="items")

    assert (db_variant.price, created_product.price, len(db_variant.items), created_product.suggested_category) == (7, 7, 1, "gta5")