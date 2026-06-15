import logging

from domain import Category
# import asyncio
# from infra.security import calculate_file_hash
from typing import Callable, Awaitable

log = logging.getLogger(__name__)


async def create_category(uow, img: bytes, file_manager, img_generator, category: Category, hash_calculator: Callable[[bytes], Awaitable[str]]):
    if category.parent_id is not None:
        async with uow:
            parent_category = await uow.db.read_one(Category, id=category.parent_id, with_raise=True, with_for_update=True)
            category.validate_parent(parent_category)
    async with file_manager.session() as files:
        file_name = await hash_calculator(img)
        #file_name = await asyncio.to_thread(calculate_file_hash, img)
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
        if category.is_folder:
            category.add_default_child()
        async with uow:
            created_category = await uow.db.create(category)
            # if created_category.is_folder:
            #     misc_category = Category(
            #         name="Прочее",
            #         is_folder=False,
            #         parent_id=created_category.id,
            #         logo_url=created_category.logo_url
            #     )
            #     await uow.db.create(misc_category)

            return created_category


async def approve_suggested_category(uow):
    async with uow:
        categories = await uow.category.get_suggested_categories_stats()
        await uow.category.upsert_suggested_categories(categories)
