import logging
# import shutil
# from pathlib import Path

import pytest
from sqlalchemy import text

from adapters.uow import UnitOfWork
from adapters.db_provider import DbProvider
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
                    users
                RESTART IDENTITY CASCADE;
                """
            )
        )
    await db_provider.close()

# @pytest.fixture(autouse=True)
# def clean_fs_after_test(request):
#     yield
#     images_path = Path("tests/images")
#     if images_path.exists() and images_path.is_dir():
#         shutil.rmtree(images_path)