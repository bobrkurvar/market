import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from adapters.db_provider import DbProvider
from adapters.http_client import HttpClient
from adapters.images import (
    CategoryImagesManager,
    ImageGenerator,
    ProductImagesManager,
)
from adapters.uow import UnitOfWork
from core import conf
from core.logger import setup_logging
from db.mapper import registry
from domain import (
    Category,
    CategoryAttr,
    Product,
    ProductItem,
    ProductVariant,
    UserRole,
)
from infra.security import async_hash_calculate
from services.auth import create_user
from services.category import create_category
from services.product import create_product


setup_logging()
log = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
SEED_PATH = SCRIPT_DIR / "seed.json"
CATEGORY_IMAGES_DIR = SCRIPT_DIR / "categories_images"
PRODUCT_IMAGES_DIR = SCRIPT_DIR / "products_images"

PRICE_FILTER_KEYS = {"price", "min_price", "max_price"}


def load_seed() -> dict[str, Any]:
    if not SEED_PATH.is_file():
        raise FileNotFoundError(f"Не найден файл с данными: {SEED_PATH}")

    with SEED_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_image(directory: Path, filename: str, entity_name: str) -> bytes:
    path = directory / filename

    if not path.is_file():
        raise FileNotFoundError(
            f"Не найдено изображение для «{entity_name}»: {path}"
        )

    return path.read_bytes()


def build_filter_config(raw_filters: list[dict[str, Any]]) -> list[CategoryAttr]:
    result: list[CategoryAttr] = []

    for raw_filter in raw_filters:
        key = raw_filter["key"]
        options = raw_filter.get("options", [])

        if key not in PRICE_FILTER_KEYS and not options:
            raise ValueError(
                f"У фильтра «{key}» должны быть варианты options."
            )

        result.append(
            CategoryAttr(
                key=key,
                label=raw_filter["label"],
                attr_type=raw_filter["type"],
                options=options,
                strict_options=raw_filter.get("strict_options", False),
            )
        )

    return result


def build_product_items(raw_items: list[str] | None) -> list[ProductItem]:
    return [
        ProductItem(content=item_content)
        for item_content in (raw_items or [])
    ]


def validate_product_category(category: Category, product_title: str) -> None:
    if category.is_folder:
        raise ValueError(
            f"Товар «{product_title}» нельзя поместить в папку "
            f"«{category.name}»."
        )


def validate_variant_attributes(
    product_title: str,
    category: Category,
    categories_by_name: dict[str, Category],
    attributes: dict[str, Any],
) -> None:
    """
    Проверяет, что вариант содержит все строгие фильтры листа и его родителей,
    а значения входят в разрешённые options.
    """
    branch: list[Category] = []
    current: Category | None = category

    while current is not None:
        branch.append(current)
        current = (
            categories_by_name.get(current.parent_name)
            if current.parent_name
            else None
        )

    for branch_category in reversed(branch):
        for category_filter in branch_category.filter_config:
            if not category_filter.strict_options:
                continue

            if category_filter.key not in attributes:
                raise ValueError(
                    f"У товара «{product_title}» отсутствует обязательный "
                    f"атрибут «{category_filter.key}»."
                )

            value = attributes[category_filter.key]
            if value not in category_filter.options:
                raise ValueError(
                    f"Значение «{value}» атрибута «{category_filter.key}» "
                    f"у товара «{product_title}» отсутствует в options "
                    f"категории «{branch_category.name}»."
                )


def preflight_validate(seed: dict[str, Any]) -> None:
    """
    Проверяет JSON и все пути к изображениям до первой записи в БД.
    Так сидер не создаст часть каталога, а потом не упадёт на отсутствующем файле.
    """
    missing_images: list[str] = []

    for category_data in seed.get("categories", []):
        image_path = CATEGORY_IMAGES_DIR / category_data["image"]
        if not image_path.is_file():
            missing_images.append(str(image_path))

    for product_data in seed.get("products", []):
        image_path = PRODUCT_IMAGES_DIR / product_data["image"]
        if not image_path.is_file():
            missing_images.append(str(image_path))

    if missing_images:
        formatted_paths = "\n".join(f"  - {item}" for item in missing_images)
        raise FileNotFoundError(
            "Не найдены изображения из seed.json:\n" + formatted_paths
        )

    category_names = [item["name"] for item in seed.get("categories", [])]
    duplicated_categories = {
        name for name in category_names if category_names.count(name) > 1
    }
    if duplicated_categories:
        raise ValueError(
            "Имена категорий должны быть уникальны: "
            + ", ".join(sorted(duplicated_categories))
        )

    category_names_set = set(category_names)
    for category_data in seed.get("categories", []):
        parent_name = category_data.get("parent")
        if parent_name and parent_name not in category_names_set:
            raise ValueError(
                f"У категории «{category_data['name']}» не найден "
                f"родитель «{parent_name}»."
            )

    user_names = [item["username"] for item in seed.get("users", [])]
    seller_names = [item["username"] for item in seed.get("sellers", [])]
    duplicate_usernames = {
        username
        for username in user_names + seller_names
        if (user_names + seller_names).count(username) > 1
    }
    if duplicate_usernames:
        raise ValueError(
            "Username должны быть уникальны: "
            + ", ".join(sorted(duplicate_usernames))
        )

    seller_names_set = set(seller_names)
    for product_data in seed.get("products", []):
        if product_data["seller"] not in seller_names_set:
            raise ValueError(
                f"У товара «{product_data['title']}» не найден продавец "
                f"«{product_data['seller']}»."
            )

        if product_data["category"] not in category_names_set:
            raise ValueError(
                f"У товара «{product_data['title']}» не найдена категория "
                f"«{product_data['category']}»."
            )


async def create_demo_users(
    seed: dict[str, Any],
    uow: UnitOfWork,
) -> tuple[dict[str, Any], dict[str, Any]]:
    users_by_username: dict[str, Any] = {}
    sellers_by_username: dict[str, Any] = {}

    log.info("Создаём demo-пользователей...")

    for user_data in seed.get("users", []):
        username = user_data["username"]

        if username in users_by_username:
            raise ValueError(f"Повторяющийся username пользователя: {username}")

        user = await create_user(
            username=username,
            password=user_data["password"],
            role=UserRole.user,
            uow=uow,
        )
        users_by_username[username] = user

    log.info("Создаём demo-продавцов...")

    for seller_data in seed.get("sellers", []):
        username = seller_data["username"]

        if username in users_by_username or username in sellers_by_username:
            raise ValueError(f"Повторяющийся username: {username}")

        seller = await create_user(
            username=username,
            password=seller_data["password"],
            role=UserRole.seller,
            uow=uow,
        )
        sellers_by_username[username] = seller

    return users_by_username, sellers_by_username


async def create_demo_categories(
    seed: dict[str, Any],
    uow: UnitOfWork,
    category_file_manager: CategoryImagesManager,
    img_generator: ImageGenerator,
) -> dict[str, Category]:
    """
    Создаёт сначала корневые категории, затем дочерние.
    `parent` в JSON — имя родительской категории.
    """
    categories_by_name: dict[str, Category] = {}
    pending = list(seed.get("categories", []))

    log.info("Создаём demo-категории...")

    while pending:
        created_this_round = 0
        next_pending: list[dict[str, Any]] = []

        for category_data in pending:
            name = category_data["name"]
            parent_name = category_data.get("parent")

            if name in categories_by_name:
                raise ValueError(f"Повторяющееся имя категории: {name}")

            if parent_name and parent_name not in categories_by_name:
                next_pending.append(category_data)
                continue

            parent = categories_by_name.get(parent_name)

            if parent is not None and not parent.is_folder:
                raise ValueError(
                    f"Категория «{name}» не может быть дочерней для листа "
                    f"«{parent.name}»."
                )

            category = Category(
                name=name,
                is_folder=category_data["is_folder"],
                parent_id=parent.id if parent else None,
                filter_config=build_filter_config(
                    category_data.get("filter_config", [])
                ),
            )

            saved_category = await create_category(
                uow=uow,
                img=read_image(
                    CATEGORY_IMAGES_DIR,
                    category_data["image"],
                    name,
                ),
                file_manager=category_file_manager,
                img_generator=img_generator,
                category=category,
                hash_calculator=async_hash_calculate,
            )

            # Сохраняем parent в доменном объекте только для валидации ветки ниже.
            saved_category.parent = parent
            saved_category.parent_id = parent.id if parent else None
            categories_by_name[name] = saved_category
            created_this_round += 1

        if created_this_round == 0:
            names = ", ".join(item["name"] for item in next_pending)
            raise ValueError(
                "Не удалось создать категории: не найдены их родители. "
                f"Проверьте поле parent: {names}"
            )

        pending = next_pending

    return categories_by_name


async def create_demo_products(
    seed: dict[str, Any],
    uow: UnitOfWork,
    sellers_by_username: dict[str, Any],
    categories_by_name: dict[str, Category],
    product_file_manager: ProductImagesManager,
    img_generator: ImageGenerator,
) -> None:
    log.info("Создаём demo-товары...")

    for product_data in seed.get("products", []):
        title = product_data["title"]
        seller_username = product_data["seller"]
        category_name = product_data["category"]

        try:
            seller = sellers_by_username[seller_username]
        except KeyError as exc:
            raise ValueError(
                f"У товара «{title}» не найден продавец «{seller_username}»."
            ) from exc

        try:
            category = categories_by_name[category_name]
        except KeyError as exc:
            raise ValueError(
                f"У товара «{title}» не найдена категория «{category_name}»."
            ) from exc

        validate_product_category(category, title)

        variants: list[ProductVariant] = []

        for variant_data in product_data.get("variants", []):
            attributes = variant_data.get("attributes", {})
            validate_variant_attributes(
                product_title=title,
                category=category,
                categories_by_name=categories_by_name,
                attributes=attributes,
            )

            # Всегда передаём список: [] для ручной выдачи, список ключей для авто.
            items = build_product_items(variant_data.get("items"))

            variants.append(
                ProductVariant(
                    price=float(variant_data["price"]),
                    attributes=attributes,
                    items=items,
                    stock=variant_data.get("stock", -1),
                    buyer_message=variant_data.get("buyer_message"),
                )
            )

        if not variants:
            raise ValueError(f"У товара «{title}» должен быть хотя бы один вариант.")

        product = Product(
            title=title,
            description=product_data.get("description", ""),
            seller_id=seller.id,
            category_id=category.id,
            variants=variants,
            buyer_message=product_data.get("buyer_message"),
        )

        await create_product(
            uow=uow,
            img=read_image(
                PRODUCT_IMAGES_DIR,
                product_data["image"],
                title,
            ),
            file_manager=product_file_manager,
            img_generator=img_generator,
            product=product,
            hash_calculator=async_hash_calculate,
        )


async def main() -> None:
    seed = load_seed()
    preflight_validate(seed)

    db_provider = DbProvider(conf.db_url)
    uow = UnitOfWork(provider=db_provider, registry=registry)
    img_generator = ImageGenerator(HttpClient(conf.image_api_url))

    try:
        _, sellers_by_username = await create_demo_users(seed, uow)

        categories_by_name = await create_demo_categories(
            seed=seed,
            uow=uow,
            category_file_manager=CategoryImagesManager(),
            img_generator=img_generator,
        )

        await create_demo_products(
            seed=seed,
            uow=uow,
            sellers_by_username=sellers_by_username,
            categories_by_name=categories_by_name,
            product_file_manager=ProductImagesManager(),
            img_generator=img_generator,
        )

        log.info(
            "✅ Demo seed завершён: пользователей=%s, продавцов=%s, "
            "категорий=%s, товаров=%s",
            len(seed.get("users", [])),
            len(seed.get("sellers", [])),
            len(seed.get("categories", [])),
            len(seed.get("products", [])),
        )
    finally:
        await db_provider.close()


if __name__ == "__main__":
    asyncio.run(main())
