import pytest
from adapters.images import ProductImagesManager, CategoryImagesManager
from adapters.files import FileManager
from .fakes import FakeStorage

@pytest.fixture
async def product_images_manager():
    return ProductImagesManager(root="tests/media", storage=FakeStorage())

@pytest.fixture
async def category_images_manager():
    return CategoryImagesManager(root="tests/media", storage=FakeStorage())

@pytest.fixture
async def file_manager():
    return FileManager(root="tests/media", storage=FakeStorage())