import logging
import shutil
from pathlib import Path

import pytest
from sqlalchemy import text
from domain import *

from adapters.uow import UnitOfWork
from adapters.db_provider import DbProvider
from adapters.images import ProductImagesManager, CategoryImagesManager
from core import conf
from db.mapper import registry

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
        await conn.execute(
            text(
                """
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
                """
            )
        )
    await db_provider.close()


@pytest.fixture(autouse=True)
def clean_fs_after_test(request):
    yield
    images_path = Path("tests/media")
    if images_path.exists() and images_path.is_dir():
        shutil.rmtree(images_path)


@pytest.fixture
async def saved_category(uow):
    async with uow:
        return await uow.db.create(Category(name="test_category", is_folder=False, logo_url=""))


@pytest.fixture
async def saved_client(uow):
    async with uow:
        return await uow.db.create(Client(username="test_client", password="password"))


@pytest.fixture
async def saved_seller(uow):
    async with uow:
        return await uow.db.create(Seller(username="test_seller", password="password"))


@pytest.fixture
async def saved_product(uow, saved_category, saved_seller):
    async with uow:
        product = Product(
            title="test_product",
            seller_id=saved_seller.id,
            category_id=saved_category.id,
            image_url="url",
            variants=ProductVariant(price=100, items=ProductItem(content="TEST-KEY-1234"))
        )

        return await uow.db.create(product)


@pytest.fixture
async def product_images_manager():
    return ProductImagesManager(root="tests/media")


@pytest.fixture
async def category_images_manager():
    return CategoryImagesManager(root="tests/media")