import base64
import logging
from binascii import Error
from functools import wraps
from pathlib import Path

from adapters.file_layers import ORIGINAL_PRODUCT, PRODUCT_IMAGE_LAYERS
from adapters.files import FileManager
from services.exceptions import ImageProcessingError
from shared import DETAILS, PRODUCTS

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
        return path_catalog.as_posix()
        #return await self.get_directory(path_catalog, base_path)

    def get_product_details_image_path(self, base_path: str) -> str:
        base_path = Path(base_path)
        name = base_path.name
        path_details = self.resolve_path(name, DETAILS)
        return path_details.as_posix()
        #return await self.get_directory(path_details, base_path)


