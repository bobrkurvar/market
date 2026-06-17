import pytest

from adapters.files import FileManager
from adapters.images import CategoryImagesManager, ProductImagesManager

from .fakes import FakeStorage, FakeUoW


@pytest.fixture
async def product_images_manager():
    return ProductImagesManager(root="tests/media", storage=FakeStorage())


@pytest.fixture
async def category_images_manager():
    return CategoryImagesManager(root="tests/media", storage=FakeStorage())


@pytest.fixture
async def file_manager():
    return FileManager(root="tests/media", storage=FakeStorage())


@pytest.fixture
async def uow():
    return FakeUoW()
