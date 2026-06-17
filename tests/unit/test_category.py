import logging

import pytest

from domain import Category, NotFoundError
from services.category import create_category
from tests.fakes import FakeImgGenerator

from .fakes import fake_name_calculate

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_not_is_folder_root_category(uow, category_images_manager):
    category: Category = await create_category(
        uow=uow,
        category=Category(name="category", is_folder=False, logo_url="url"),
        img=b"a",
        file_manager=category_images_manager,
        img_generator=FakeImgGenerator(),
        hash_calculator=fake_name_calculate,
    )
    with pytest.raises(NotFoundError):
        async with uow:
            assert await uow.db.read_one(
                Category, parent_id=category.id, name="Прочее", with_raise=True
            )
    assert category is not None
    assert category.logo_url != "url"


@pytest.mark.asyncio
async def test_create_subcategory_with_current_category(uow, category_images_manager):
    parent_category: Category = await create_category(
        uow=uow,
        category=Category(name="parent", is_folder=True),
        img=b"ab",
        file_manager=category_images_manager,
        img_generator=FakeImgGenerator(),
        hash_calculator=fake_name_calculate,
    )
    created_category: Category = await create_category(
        uow=uow,
        category=Category(
            name="category",
            is_folder=False,
            logo_url="url",
            parent_id=parent_category.id,
        ),
        img=b"a",
        file_manager=category_images_manager,
        img_generator=FakeImgGenerator(),
        hash_calculator=fake_name_calculate,
    )
    assert created_category.parent_id == parent_category.id


@pytest.mark.asyncio
async def test_create_subcategory_with_wrong_category(uow, category_images_manager):
    parent_category: Category = await create_category(
        uow=uow,
        category=Category(name="parent", is_folder=False),
        img=b"a",
        file_manager=category_images_manager,
        img_generator=FakeImgGenerator(),
        hash_calculator=fake_name_calculate,
    )
    with pytest.raises(ValueError, match="Нельзя создать"):
        await create_category(
            uow=uow,
            category=Category(
                name="category",
                is_folder=False,
                logo_url="url",
                parent_id=parent_category.id,
            ),
            img=b"a",
            file_manager=category_images_manager,
            img_generator=FakeImgGenerator(),
            hash_calculator=fake_name_calculate,
        )
