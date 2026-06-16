import os
import random
import logging
import asyncio
from faker import Faker
from db.mapper import registry
from domain import Category, Product, UserRole, ProductVariant, ProductItem
from core.logger import setup_logging
from services.category import create_category
from services.product import create_product
from services.auth import create_user
from core import conf
from adapters.uow import UnitOfWork
from adapters.http_client import HttpClient
from adapters.db_provider import DbProvider
from adapters.images import ImageGenerator, ProductImagesManager, CategoryImagesManager
from infra.security import async_hash_calculate

setup_logging()

log = logging.getLogger(__name__)
fake = Faker(['ru_RU', 'en_US'])

SOURCE_CAT_DIR = "scripts/seed_categories"
SOURCE_PROD_DIR = "scripts/seed_products"


FOLDER_FILTERS_POOL = [
    [
        {"key": "platform", "label": "Платформа", "type": "checkbox", "options": ["Steam", "Epic Games", "Origin"]},
        {"key": "region", "label": "Регион активации", "type": "select", "options": ["Global", "Turkey", "CIS"]}
    ],
    [
        {"key": "os", "label": "Операционная система", "type": "radio", "options": ["Windows 11", "Windows 10", "macOS"]},
        {"key": "duration", "label": "Срок действия", "type": "select", "options": ["1 месяц", "12 месяцев", "Навсегда"]}
    ]
]

LEAF_FILTERS_POOL = [
    [{"key": "edition", "label": "Издание", "type": "checkbox", "options": ["Standard", "Deluxe", "Ultimate"]}],
    [{"key": "language", "label": "Язык", "type": "select", "options": ["Русский", "English", "Multilanguage"]}],
    []  # Лист может и не иметь уникальных фильтров, наследуя только родительские
]



def get_files_from_dir(directory: str) -> list[str]:
    """Безопасно получает список файлов из папки"""
    if os.path.exists(directory):
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return []


cat_images_pool = get_files_from_dir(SOURCE_CAT_DIR)
prod_images_pool = get_files_from_dir(SOURCE_PROD_DIR)


async def seed_data(uow, product_file_manager, category_file_manager, img_generator):
    log.info("Начинаем генерацию презентабельных данных...")

    # --- 1. ГЕНЕРАЦИЯ ПРОДАВЦОВ ---
    log.info("Создаем продавцов...")
    sellers = []

    for _ in range(5):
        seller = await create_user(
            username=fake['en_US'].user_name(),
            password="password",
            role=UserRole.seller,
            uow=uow
        )
        sellers.append(seller)

    log.info(f"✅ Создано продавцов: {len(sellers)}")

    # --- 2. ГЕНЕРАЦИЯ КАТЕГОРИЙ (Папки и Листы) ---
    log.info("Создаем корневые категории (Папки)...")
    folder_categories = []

    for _ in range(2):
        img_filename = random.choice(cat_images_pool)
        with open(os.path.join(SOURCE_CAT_DIR, img_filename), "rb") as f:
            img_bytes = f.read()

        filter_config = random.choice(FOLDER_FILTERS_POOL)

        saved_folder = await create_category(
            uow=uow,
            img=img_bytes,
            file_manager=category_file_manager,
            img_generator=img_generator,
            category=Category(
                name=fake['ru_RU'].word().capitalize(),
                is_folder=True,
                filter_config=filter_config
            ),
            hash_calculator=async_hash_calculate
        )
        folder_categories.append(saved_folder)

    log.info("Создаем конечные категории (Листы)...")
    leaf_categories = []

    for _ in range(4):
        parent_folder = random.choice(folder_categories)
        img_filename = random.choice(cat_images_pool)
        with open(os.path.join(SOURCE_CAT_DIR, img_filename), "rb") as f:
            img_bytes = f.read()

        filter_config = random.choice(LEAF_FILTERS_POOL)

        saved_leaf = await create_category(
            uow=uow,
            img=img_bytes,
            file_manager=category_file_manager,
            img_generator=img_generator,
            category=Category(
                name=fake['ru_RU'].word().capitalize(),
                is_folder=False,
                parent_id=parent_folder.id,
                filter_config=filter_config
            ),
            hash_calculator=async_hash_calculate
        )
        leaf_categories.append(saved_leaf)

    log.info(f"✅ Создано папок: {len(folder_categories)}, листов: {len(leaf_categories)}")

    # --- 3. ГЕНЕРАЦИЯ ТОВАРОВ ---
    log.info("Создаем товары...")
    products_to_create = 60

    for i in range(1, products_to_create + 1):
        seller = random.choice(sellers)
        category = random.choice(leaf_categories)

        # Находим папку-родителя, чтобы собрать ключи для атрибутов (имитация слияния фильтров)
        parent_folder = next(f for f in folder_categories if f.id == category.parent_id)

        # Собираем ключи, которые обязаны быть в варианте, чтобы он отобразился в фильтрах
        expected_keys = [f["key"] for f in parent_folder.filter_config] + [f["key"] for f in category.filter_config]

        img_filename = random.choice(prod_images_pool)
        with open(os.path.join(SOURCE_PROD_DIR, img_filename), "rb") as f:
            img_bytes = f.read()

        num_variants = random.randint(1, 3)
        product_variants = []

        for _ in range(num_variants):
            keys_to_create = random.randint(5, 15)
            product_items = []

            for _ in range(keys_to_create):
                key_content = fake.bothify(text='?????-?????-?????', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                item = ProductItem(content=key_content)
                product_items.append(item)

            # Формируем реалистичные атрибуты варианта на основе ключей категории
            variant_attributes = {}
            for key in expected_keys:
                if key == "platform":
                    variant_attributes[key] = random.choice(["Steam", "Epic Games", "Origin"])
                elif key == "region":
                    variant_attributes[key] = random.choice(["Global", "Turkey", "CIS"])
                elif key == "os":
                    variant_attributes[key] = random.choice(["Windows 11", "Windows 10", "macOS"])
                elif key == "duration":
                    variant_attributes[key] = random.choice(["1 месяц", "12 месяцев", "Навсегда"])
                elif key == "edition":
                    variant_attributes[key] = random.choice(["Standard", "Deluxe", "Ultimate"])
                elif key == "language":
                    variant_attributes[key] = random.choice(["Русский", "English", "Multilanguage"])
                else:
                    variant_attributes[key] = fake.word().capitalize()

            # Добавляем свободный "информационный" атрибут, который не участвует в фильтрах
            variant_attributes["Доставка"] = "Моментальная"

            variant = ProductVariant(
                price=float(random.randint(99, 4999)),
                attributes=variant_attributes,
                items=product_items
            )
            product_variants.append(variant)

        product = Product(
            title=f"{fake['en_US'].word().capitalize()} {fake['en_US'].word().capitalize()}",
            description=fake['ru_RU'].text(max_nb_chars=400),
            seller_id=seller.id,
            category_id=category.id,
            variants=product_variants
        )

        await create_product(
            uow=uow,
            img=img_bytes,
            file_manager=product_file_manager,
            img_generator=img_generator,
            product=product,
            hash_calculator=async_hash_calculate
        )

    log.info(f"✅ Создано товаров: {products_to_create}")
    log.info("🎉 Генерация полностью завершена!")


if __name__ == "__main__":
    db_provider = DbProvider(conf.db_url)
    uow = UnitOfWork(provider=db_provider, registry=registry)
    img_generator = ImageGenerator(HttpClient(conf.image_api_url))
    asyncio.run(seed_data(
        uow=uow,
        img_generator=img_generator,
        product_file_manager=ProductImagesManager(),
        category_file_manager=CategoryImagesManager()
    ))