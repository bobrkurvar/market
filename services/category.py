import logging

from domain import Category
import asyncio
from infra.security import calculate_file_hash
from domain import Operations, Operation

log = logging.getLogger(__name__)


async def create_category(uow, img: bytes, file_manager, img_generator, category: Category):
    if category.parent_id is not None:
        async with uow:
            parent_category = await uow.db.read_one(Category, id=category.parent_id, with_raise=True)
            category.validate_parent(parent_category)
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
            created_category = await uow.db.create(category)
            if created_category.is_folder:
                misc_category = Category(
                    name="Прочее",
                    is_folder=False,
                    parent_id=created_category.id,
                    logo_url=created_category.logo_url
                )
                await uow.db.create(misc_category)

            return created_category


async def approve_suggested_category(uow):
    """
    Нужно как-то оптимизировать ведь нет особого желания проходится по всем продуктам ради поиска нескольких
    Ну или может итак оптимально
    """
    category_condition = Operation(value=None, op=Operations.is_not)
    suggested_categories = await uow.read(Category, suggested_category=category_condition)
