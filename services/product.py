import logging

from domain import Product
from infra.matcher import normalize_category_name
from typing import Callable, Awaitable

log = logging.getLogger(__name__)


async def create_product(uow, img: bytes, file_manager, img_generator, product: Product, hash_calculator: Callable[[bytes], Awaitable[str]]):
    async with file_manager.session() as files:
        #file_name = await asyncio.to_thread(calculate_file_hash, img)
        file_name = await hash_calculator(img)
        image_path = file_manager.base_product_path(file_name)
        log.debug("save file by path: %s", str(image_path))
        try:
            await files.save(image_path, img)
            miniatures = await img_generator.generate_product_variants(img)
            for layer, miniature in miniatures.items():
                await files.save_by_layer(file_name, miniature, layer)
        except FileExistsError:
            log.debug("путь %s уже занять", str(image_path))

        product.image_url = str(image_path)
        product.suggested_category = normalize_category_name(product.suggested_category)
        async with uow:
            return await uow.db.create(product)