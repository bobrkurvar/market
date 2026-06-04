import logging

from domain import Category
import asyncio
from infra.security import calculate_file_hash

log = logging.getLogger(__name__)


async def create_category(uow, img: bytes, file_manager, img_generator, category: Category):
    async with file_manager.session() as files:
        file_name = await asyncio.to_thread(calculate_file_hash, img)
        image_path = file_manager.base_category_path(file_name)
        log.debug("save file by path: %s", str(image_path))
        try:
            await files.save(image_path, img)
            miniatures = await img_generator.generate_category_variants(img)
            for layer, miniature in miniatures.items():
                await files.save_by_layer(file_name, miniature, layer)
        except FileExistsError:
            log.debug("путь %s уже занять", str(image_path))

        category.logo_url = str(image_path)
        async with uow:
            return await uow.db.create(category)