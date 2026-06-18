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

def is_variant_matching(variant, min_price, max_price, filters):
    if min_price is not None and variant.price < min_price:
        return False
    if max_price is not None and variant.price > max_price:
        return False

    for key, value in filters.items():
        attr_val = variant.attributes.get(key)

        if not attr_val:
            return False

        if isinstance(value, list):
            if attr_val not in value:
                return False
        else:
            if attr_val != str(value):
                return False

    return True

async def search_and_filter_products(
    uow,
    limit: int,
    offset: int,
    min_price: float | None = None,
    max_price: float | None = None,
    category_id: int | None = None,
    q: str | None = None,
    **filters
):
    async with uow:
        products, count = await uow.product.get_filtered_products(
            q=q,
            category_id=category_id,
            limit=limit,
            offset=offset,
            min_price=min_price,
            max_price=max_price,
            **filters
        )
    # Сортировка вариантов внутри продукта, что бы вариант подходил по фильтрам, а если фильтров нет то будут самый минимальный по цене
    for product in products:
        product.variants.sort(key=lambda v: (
            not is_variant_matching(v, min_price, max_price, filters),
            v.price
        ))
    return products, count
