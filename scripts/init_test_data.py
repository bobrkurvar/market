import asyncio
import logging
import random
import string

from domain import Category, Product, ProductVariant, ProductItem
from adapters.db_provider import DbProvider
from adapters.uow import UnitOfWork
from db.mapper import registry
from services.category import create_category
from services.product import create_product
from adapters.images import CategoryImagesManager, ProductImagesManager, ImageGenerator
from adapters.http_client import HttpClient
from core.logger import setup_logging
from core import conf

setup_logging()

log = logging.getLogger(__name__)

# ==========================================
# НАСТРОЙКИ МАССОВОСТИ (МЕНЯЙ ПОД СЕБЯ)
# ==========================================
NUM_CATEGORIES = 10  # Сколько создать категорий
PRODUCTS_PER_CAT = 3  # Сколько товаров в КАЖДОЙ категории
VARIANTS_PER_PRODUCT = (1, 3)  # Рандомный разброс количества опций у одного товара
KEYS_PER_VARIANT = (5, 20)  # Рандомное количество ключей в каждой опции
SELLER_ID = 1  # ID продавца, на которого вешаем товары


# ==========================================

def generate_random_key():
    """Генерирует фейковый ключ формата XXXX-YYYY-ZZZZ"""
    return '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))


async def seed_mass_data(uow, http_client):
    cat_file_manager = CategoryImagesManager()
    prod_file_manager = ProductImagesManager()
    img_generator = ImageGenerator(http_client)


    dummy_img = (
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!"
        b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    )

    log.info(f"🚀 Запуск массовой генерации данных...")

    created_categories = []
    for c in range(1, NUM_CATEGORIES + 1):
        cat = Category(name=f"Категория {c}")

        saved_cat = await create_category(uow, dummy_img, cat_file_manager, img_generator, cat)
        created_categories.append(saved_cat)
        log.info(f"📁 Создана: {saved_cat.name} (ID: {saved_cat.id})")

    total_products = 0
    total_keys = 0

    for cat in created_categories:
        log.info(f"⏳ Заполняем '{cat.name}' товарами ({PRODUCTS_PER_CAT} шт.)...")

        for p in range(1, PRODUCTS_PER_CAT + 1):

            variants = []
            num_variants = random.randint(*VARIANTS_PER_PRODUCT)

            # Генерация опций (вариантов) товара
            for v in range(1, num_variants + 1):
                num_keys = random.randint(*KEYS_PER_VARIANT)
                items = [ProductItem(content=generate_random_key()) for _ in range(num_keys)]
                total_keys += num_keys

                variants.append(
                    ProductVariant(
                        price=float(random.randint(50, 9990)),
                        attributes={
                            "Издание": f"Вариант {v}",
                            "Регион": random.choice(["Global", "RU/CIS", "EU", "USA"])
                        },
                        items=items
                    )
                )

            # Собираем сам товар
            product = Product(
                title=f"Product {cat.id}-{p} [Mass Gen]",
                description=f"Это автоматически сгенерированный товар №{p} из {cat.name}.\n"
                            f"Он нужен для тестирования верстки и пагинации.",
                category_id=cat.id,
                seller_id=SELLER_ID,
                variants=variants
            )

            # Прогоняем через сервис (сохранит картинки и сложит всё в БД)
            await create_product(uow, dummy_img, prod_file_manager, img_generator, product)
            total_products += 1


    log.info(f"🎉 ГОТОВО! Успешно создано:")
    log.info(f"   - Категорий: {NUM_CATEGORIES}")
    log.info(f"   - Товаров: {total_products}")
    log.info(f"   - Ключей в базе: {total_keys}")


if __name__ == "__main__":
    provider = DbProvider(conf.db_url)
    uow = UnitOfWork(session_factory=provider.session_factory, registry=registry)
    http_client = HttpClient(url=conf.image_api_url)
    asyncio.run(seed_mass_data(uow=uow, http_client=http_client))