from pathlib import Path

import pytest
from shared import DETAILS, PRODUCTS, CATEGORY_CATALOG, CATEGORY_SEARCH


@pytest.mark.asyncio
async def test_files_session_remove_exists_files_when_raises(file_manager):
    try:
        async with file_manager.session() as files:
            await files.save("image1", b"1")
            await files.save("image2", b"2")
            await files.save_by_layer("image3", b"3", PRODUCTS)
            assert len(file_manager._storage) == 3
            raise Exception
    except Exception:
        assert not file_manager._storage


def test_base_product_path(product_images_manager):
    file_name = "abcdef123456.jpg"
    path = product_images_manager.base_product_path(file_name)
    expected_path = Path(f"{product_images_manager._root}/base/products/{file_name}")
    assert path == expected_path


def test_base_catalog_path(category_images_manager):
    file_name = "abcdef123456.jpg"
    path = category_images_manager.base_category_path(file_name)
    expected_path = Path(f"{category_images_manager._root}/base/categories/{file_name}")
    assert path == expected_path

def test_resolve_path_for_category_catalog_layer(category_images_manager):
    file_name = "abcdef123456.jpg"
    layer = CATEGORY_CATALOG
    path = category_images_manager.resolve_path(file_name, layer)
    expected_path = Path(f"{category_images_manager._root}/categories/catalog/{file_name}")
    assert path == expected_path


def test_resolve_path_for_category_search_layer(category_images_manager):
    file_name = "abcdef123456.jpg"
    layer = CATEGORY_SEARCH
    path = category_images_manager.resolve_path(file_name, layer)
    expected_path = Path(f"{category_images_manager._root}/categories/search/{file_name}")
    assert path == expected_path


def test_resolve_path_for_product_catalog_layer(product_images_manager):
    file_name = "abcdef123456.jpg"
    layer = PRODUCTS
    path = product_images_manager.resolve_path(file_name, layer)
    expected_path = Path(f"{product_images_manager._root}/products/catalog/{file_name}")
    assert path == expected_path


def test_resolve_path_for_product_details_layer(product_images_manager):
    file_name = "abcdef123456.jpg"
    layer = DETAILS
    path = product_images_manager.resolve_path(file_name, layer)
    expected_path = Path(f"{product_images_manager._root}/products/details/{file_name}")
    assert path == expected_path


@pytest.mark.asyncio
async def test_save_file_product_catalog_path(product_images_manager):
    file_name, img, layer = "abcdef123456.jpg", b"aaa", PRODUCTS
    await product_images_manager.save_by_layer(file_name, img, layer)
    expected_path = Path(f"{product_images_manager._root}/products/catalog/{file_name}").as_posix()
    assert expected_path in product_images_manager._storage.fs


@pytest.mark.asyncio
async def test_save_file_product_details_path(product_images_manager):
    file_name, img, layer = "abcdef123456.jpg", b"aaa", DETAILS
    await product_images_manager.save_by_layer(file_name, img, layer)
    expected_path = Path(f"{product_images_manager._root}/products/details/{file_name}").as_posix()
    assert expected_path in product_images_manager._storage.fs
