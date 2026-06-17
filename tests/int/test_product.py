import logging

import pytest

from domain import Product, ProductItem, ProductVariant
from infra.security import async_hash_calculate
from services.product import create_product
from tests.fakes import FakeImgGenerator

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_product_in_category_without_attrs(
    uow, saved_client, saved_seller, saved_category_without_attrs, product_images_manager
):
    product = Product(
        title="title",
        seller=saved_seller,
        variants=ProductVariant(price=7, items=ProductItem(content="content")),
        category_id=saved_category_without_attrs.id,
        image_url="url",
        suggested_category="  GTA 5  ",
    )
    created_product: Product = await create_product(
        uow=uow,
        product=product,
        img=b"a",
        file_manager=product_images_manager,
        img_generator=FakeImgGenerator(),
        hash_calculator=async_hash_calculate,
    )

    assert created_product is not None
    assert created_product.image_url != "url"
    async with uow:
        db_product = await uow.db.read_one(
            Product, id=created_product.id, loaded="variants"
        )
        db_variant = await uow.db.read_one(
            ProductVariant, product_id=created_product.id, loaded="items"
        )
    assert (db_product.price, len(db_variant.items), db_product.suggested_category) == (
        7,
        1,
        "gta5",
    )


@pytest.mark.parametrize(
    "invalid_attributes, expected_error_match",
    [
        # Сценарий 1: Пропустили обязательное поле 'region'
        (
                {"platform": "Steam"},
                "Обязательная характеристика 'Регион' не заполнена"
        ),
        # Сценарий 2: Прислали вообще пустые атрибуты
        (
                {},
                "Обязательная характеристика"
        ),
        # Сценарий 3: Неверное значение (строка) для Платформы
        (
                {"platform": "Origin", "region": "CIS"},
                "Значение 'Origin' недопустимо для 'Платформа'"
        ),
        # Сценарий 4: Одно из значений в массиве невалидно (EU нет в списке)
        (
                {"platform": "Steam", "region": ["CIS", "EU"]},
                "Значение 'EU' недопустимо для 'Регион'"
        ),
        # Сценарий 5: Опечатка в регистре (если мы требуем точного совпадения)
        (
                {"platform": "steam", "region": "Global"},
                "Значение 'steam' недопустимо для 'Платформа'"
        ),
    ]
)
@pytest.mark.asyncio
async def test_create_product_fails_on_invalid_attrs(
    uow,
    saved_seller,
    saved_category_with_strict_attrs,
    product_images_manager,
    invalid_attributes,  # Инжектится из parametrize
    expected_error_match  # Инжектится из parametrize
):
    invalid_product = Product(
        title="Invalid Game",
        seller=saved_seller,
        category_id=saved_category_with_strict_attrs.id,
        image_url="url",
        variants=[
            ProductVariant(
                price=100,
                items=[ProductItem(content="key")],
                attributes=invalid_attributes
            )
        ]
    )

    with pytest.raises(ValueError, match=expected_error_match):
        await create_product(
            uow=uow,
            product=invalid_product,
            img=b"a",
            file_manager=product_images_manager,
            img_generator=FakeImgGenerator(),
            hash_calculator=async_hash_calculate,
        )