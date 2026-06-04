import base64
import logging
from binascii import Error
from functools import wraps
from pathlib import Path

from adapters.file_layers import ORIGINAL_PRODUCT, PRODUCT_IMAGE_LAYERS, CATEGORY_IMAGE_LAYERS, ORIGINAL_CATEGORY
from adapters.files import FileManager
from services.exceptions import ImageProcessingError
from shared import DETAILS, PRODUCTS, CATEGORY_CATALOG, CATEGORY_SEARCH

# import aiofiles # type: ignore


log = logging.getLogger(__name__)


def generate_image_with_exc(generate):
    @wraps(generate)
    async def wrapper(*args, **kwargs):
        try:
            result = await generate(*args, **kwargs)
        except (ValueError, Error) as exc:
            raise ImageProcessingError("Ошибка декодирования") from exc
        if result is None:
            raise ImageProcessingError("Ошибка генерации")
        return result

    return wrapper


class ImageGenerator:
    def __init__(self, api_client):
        self._api_client = api_client

    @generate_image_with_exc
    async def generate_product_variants(self, img: bytes):
        img = base64.b64encode(img).decode("utf-8")
        response = await self._api_client.generate_images(
            data=img, targets=(PRODUCTS, DETAILS)
        )
        response[PRODUCTS] = base64.b64decode(response[PRODUCTS])
        response[DETAILS] = base64.b64decode(response[DETAILS])
        return response

    @generate_image_with_exc
    async def generate_category_variants(self, img: bytes):
        img = base64.b64encode(img).decode("utf-8")
        response = await self._api_client.generate_images(
            data=img, targets=(CATEGORY_CATALOG, CATEGORY_SEARCH)
        )
        response[CATEGORY_CATALOG] = base64.b64decode(response[CATEGORY_CATALOG])
        response[CATEGORY_SEARCH] = base64.b64decode(response[CATEGORY_SEARCH])
        return response


class ProductImagesManager(FileManager):

    def __init__(self, storage=None):
        super().__init__(PRODUCT_IMAGE_LAYERS, storage)

    async def delete_product(self, base_path: str | Path) -> int:
        return await self.delete_by_layers(base_path, [PRODUCTS, DETAILS])

    def base_product_path(self, file_name: str) -> Path:
        return self.resolve_path(file_name, ORIGINAL_PRODUCT)

    def get_product_catalog_image_path(self, base_path: str) -> str:
        base_path = Path(base_path)
        name = base_path.name
        path_catalog = self.resolve_path(name, PRODUCTS)
        return f"/{path_catalog.as_posix()}"

    def get_product_details_image_path(self, base_path: str) -> str:
        base_path = Path(base_path)
        name = base_path.name
        path_details = self.resolve_path(name, DETAILS)
        return f"/{path_details.as_posix()}"


class CategoryImagesManager(FileManager):

    def __init__(self, storage=None):
        super().__init__(CATEGORY_IMAGE_LAYERS, storage)

    async def delete_category(self, base_path: str | Path) -> int:
        return await self.delete_by_layers(base_path, [CATEGORY_CATALOG, CATEGORY_SEARCH])

    def base_category_path(self, file_name: str) -> Path:
        return self.resolve_path(file_name, ORIGINAL_CATEGORY)

    def get_category_catalog_image_path(self, base_path: str) -> str:
        base_path = Path(base_path)
        name = base_path.name
        path_catalog = self.resolve_path(name, CATEGORY_CATALOG)
        return f"/{path_catalog.as_posix()}"

    def get_category_search_image_path(self, base_path: str) -> str:
        base_path = Path(base_path)
        name = base_path.name
        path_search = self.resolve_path(name, CATEGORY_SEARCH)
        return f"/{path_search.as_posix()}"



