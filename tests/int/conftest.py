import logging
import shutil
from pathlib import Path

import pytest
from sqlalchemy import text

from adapters.db_provider import DbProvider
from adapters.images import CategoryImagesManager, ProductImagesManager
from adapters.uow import UnitOfWork
from core import conf
from db.mapper import registry
from domain import *

log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
async def db_provider():
    provider = DbProvider(conf.test_db_url)
    yield provider
    await provider.close()


@pytest.fixture
async def uow(request, db_provider):
    uow = UnitOfWork(registry=registry, session_factory=db_provider.session_factory)

    yield uow

    async with db_provider.engine.begin() as conn:
        await conn.execute(text("""
                TRUNCATE
                    product_items,
                    products,
                    orders,
                    clients,
                    sellers,
                    users,
                    categories,
                    suggested_categories
                RESTART IDENTITY CASCADE;
                """))
    await db_provider.close()


@pytest.fixture(autouse=True)
def clean_fs_after_test(request):
    yield
    images_path = Path("tests/media")
    if images_path.exists() and images_path.is_dir():
        shutil.rmtree(images_path)


@pytest.fixture
async def saved_category_without_attrs(uow):
    async with uow:
        return await uow.db.create(
            Category(name="test_category", is_folder=False, logo_url="")
        )


@pytest.fixture
async def saved_category_with_strict_attrs(uow):
    filter_config = [
        CategoryAttr(
            key="platform",
            label="Платформа",
            strict_options=True,
            options=["Steam", "Epic Games"],
            attr_type="select"
        ),
        CategoryAttr(
            key="region",
            label="Регион",
            strict_options=True,
            options=["CIS", "Global"],
            attr_type="select"
        ),
        CategoryAttr(
            key="os",
            label="Операционная система",
            strict_options=False,
            options=["Windows 10"],
            attr_type="checkbox"
        )
    ]

    async with uow:
        return await uow.db.create(
            Category(
                name="Игры с фильтрами",
                is_folder=False,
                logo_url="",
                filter_config=filter_config
            )
        )



@pytest.fixture
async def saved_client(uow):
    async with uow:
        return await uow.db.create(Client(username="test_client", password="password"))


@pytest.fixture
async def saved_seller(uow):
    async with uow:
        return await uow.db.create(Seller(username="test_seller", password="password"))


@pytest.fixture
async def saved_product(uow, saved_category_without_attrs, saved_seller):
    async with uow:
        product = Product(
            title="test_product",
            seller_id=saved_seller.id,
            category_id=saved_category_without_attrs.id,
            image_url="url",
            variants=ProductVariant(
                price=100, items=ProductItem(content="TEST-KEY-1234")
            ),
        )

        return await uow.db.create(product)


@pytest.fixture
async def product_images_manager():
    return ProductImagesManager(root="tests/media")


@pytest.fixture
async def category_images_manager():
    return CategoryImagesManager(root="tests/media")
