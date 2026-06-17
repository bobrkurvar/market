import logging
from typing import Awaitable, Callable

from domain import Product
from infra.matcher import normalize_category_name

log = logging.getLogger(__name__)


async def create_product(
    uow,
    img: bytes,
    file_manager,
    img_generator,
    product: Product,
    hash_calculator: Callable[[bytes], Awaitable[str]],
):
    async with uow:
        ancestors = await uow.category.get_category_branch(product.category_id)
    if not ancestors:
        raise ValueError("Указанная категория не найдена.")

    strict_filters = {}
    for cat in ancestors:
        strict_filters.update(cat.strict_filters_dict)

    for variant in product.variants:
        for req_key, rule in strict_filters.items():
            if req_key not in variant.attributes:
                raise ValueError(f"Обязательная характеристика '{rule['label']}' не заполнена.")
            val = variant.attributes[req_key]
            if isinstance(val, list):
                for item in val:
                    if item not in rule['options']:
                        raise ValueError(f"Значение '{item}' недопустимо для '{rule['label']}'. Доступные: {', '.join(rule['options'])}")
            else:
                if val not in rule['options']:
                    raise ValueError(f"Значение '{val}' недопустимо для '{rule['label']}'. Доступные: {', '.join(rule['options'])}")

    async with file_manager.session() as files:
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
