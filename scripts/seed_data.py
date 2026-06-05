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

setup_logging()

log = logging.getLogger(__name__)
fake = Faker(['ru_RU', 'en_US'])

SOURCE_CAT_DIR = "scripts/seed_categories"
SOURCE_PROD_DIR = "scripts/seed_products"


def get_files_from_dir(directory: str) -> list[str]:
    """Безопасно получает список файлов из папки"""
    if os.path.exists(directory):
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return []


cat_images_pool = get_files_from_dir(SOURCE_CAT_DIR)
prod_images_pool = get_files_from_dir(SOURCE_PROD_DIR)



async def seed_data(uow, product_file_manager, category_file_manager, img_generator):
    log.info("Начинаем генерацию презентабельных данных...")

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

    # --- 2. ГЕНЕРАЦИЯ КАТЕГОРИЙ
    log.info("Создаем категории...")
    categories = []

    for _ in range(6):
        img_filename = random.choice(cat_images_pool)
        with open(os.path.join(SOURCE_CAT_DIR, img_filename), "rb") as f:
            img_bytes = f.read()

        saved_cat = await create_category(
            uow=uow,
            img=img_bytes,
            file_manager=category_file_manager,
            img_generator=img_generator,
            category=Category(name=fake['ru_RU'].word().capitalize())
        )
        categories.append(saved_cat)

    log.info(f"✅ Создано категорий: {len(categories)}")

    # --- 3. ГЕНЕРАЦИЯ ТОВАРОВ ---
    log.info("Создаем товары...")
    products_to_create = 60

    for i in range(1, products_to_create + 1):
        seller = random.choice(sellers)
        category = random.choice(categories)
        img_filename = random.choice(prod_images_pool)
        with open(os.path.join(SOURCE_PROD_DIR, img_filename), "rb") as f:
            img_bytes = f.read()

        num_variants = random.randint(1, 3)
        product_variants = []

        for _ in range(num_variants):
            # Генерируем ключи (айтемы) для этого конкретного варианта
            keys_to_create = random.randint(5, 15)
            product_items = []

            for _ in range(keys_to_create):
                key_content = fake.bothify(text='?????-?????-?????', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                item = ProductItem(content=key_content)
                product_items.append(item)

            variant = ProductVariant(
                price=float(random.randint(99, 4999)),
                attributes={"edition": f"{fake['en_US'].word().capitalize()} Edition"},
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
            product=product
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