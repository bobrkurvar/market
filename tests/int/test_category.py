import logging

import pytest

from domain import Category, NotFoundError
from infra.security import async_hash_calculate
from services.category import create_category
from tests.fakes import FakeImgGenerator

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_is_folder_root_category(uow, category_images_manager):
    category: Category = await create_category(
        uow=uow,
        category=Category(name="category", is_folder=True, logo_url="url"),
        img=b"a",
        file_manager=category_images_manager,
        img_generator=FakeImgGenerator(),
        hash_calculator=async_hash_calculate,
    )
    async with uow:
        child_category = await uow.db.read_one(
            Category, parent_id=category.id, name="Прочее", with_raise=True
        )
    assert child_category.logo_url == category.logo_url
    assert category is not None
    assert category.logo_url != "url"
