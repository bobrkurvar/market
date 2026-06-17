# import asyncio
# import logging
# import random
# import string
#
# from domain import Category, Product, ProductVariant, ProductItem, Seller
# from adapters.db_provider import DbProvider
# from adapters.uow import UnitOfWork
# from db.mapper import registry
# from services.category import create_category
# from services.product import create_product
# from adapters.images import CategoryImagesManager, ProductImagesManager, ImageGenerator
# from adapters.http_client import HttpClient
# from core.logger import setup_logging
# from core import conf
#
# setup_logging()
#
# log = logging.getLogger(__name__)
#
#
# NUM_CATEGORIES = 10  # Сколько создать категорий
# PRODUCTS_PER_CAT = 3  # Сколько товаров в КАЖДОЙ категории
# VARIANTS_PER_PRODUCT = (1, 3)  # Рандомный разброс количества опций у одного товара
# KEYS_PER_VARIANT = (5, 20)  # Рандомное количество ключей в каждой опции
#
#
#
# def generate_random_key():
#     """Генерирует фейковый ключ формата XXXX-YYYY-ZZZZ"""
#     return '-'.join(''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))
#
#
# async def seed_mass_data(uow, http_client):
#     cat_file_manager = CategoryImagesManager()
#     prod_file_manager = ProductImagesManager()
#     img_generator = ImageGenerator(http_client)
#
#
#     dummy_img = (
#         b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!"
#         b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
#     )
#
#     log.info(f"🚀 Запуск массовой генерации данных...")
#     log.info("👤 Проверка/создание тестового продавца...")
#     try:
#         async with uow:
#             seller = Seller(username="seller1", password="password")
#             seller = await uow.db.create(seller)
#             log.info(f"✅ Продавец с ID={seller.id} успешно создан!")
#     except:
#         pass
#     created_categories = []
#     for c in range(1, NUM_CATEGORIES + 1):
#         cat = Category(name=f"Категория {c}")
#         try:
#             saved_cat = await create_category(uow, dummy_img, cat_file_manager, img_generator, cat)
#             created_categories.append(saved_cat)
#         except:
#             pass
#
#     total_products = 0
#     total_keys = 0
#
#     for cat in created_categories:
#         log.info(f"⏳ Заполняем '{cat.name}' товарами ({PRODUCTS_PER_CAT} шт.)...")
#
#         for p in range(1, PRODUCTS_PER_CAT + 1):
#
#             variants = []
#             num_variants = random.randint(*VARIANTS_PER_PRODUCT)
#
#             # Генерация опций (вариантов) товара
#             for v in range(1, num_variants + 1):
#                 num_keys = random.randint(*KEYS_PER_VARIANT)
#                 items = [ProductItem(content=generate_random_key()) for _ in range(num_keys)]
#                 total_keys += num_keys
#
#                 variants.append(
#                     ProductVariant(
#                         price=float(random.randint(50, 9990)),
#                         attributes={
#                             "Издание": f"Вариант {v}",
#                             "Регион": random.choice(["Global", "RU/CIS", "EU", "USA"])
#                         },
#                         items=items
#                     )
#                 )
#
#             # Собираем сам товар
#             product = Product(
#                 title=f"Product {cat.id}-{p} [Mass Gen]",
#                 description=f"Это автоматически сгенерированный товар №{p} из {cat.name}.\n"
#                             f"Он нужен для тестирования верстки и пагинации.",
#                 category_id=cat.id,
#                 seller_id=seller.id,
#                 variants=variants
#             )
#
#             # Прогоняем через сервис (сохранит картинки и сложит всё в БД)
#             await create_product(uow, dummy_img, prod_file_manager, img_generator, product)
#             total_products += 1
#
#
#     log.info(f"🎉 ГОТОВО! Успешно создано:")
#     log.info(f"   - Категорий: {NUM_CATEGORIES}")
#     log.info(f"   - Товаров: {total_products}")
#     log.info(f"   - Ключей в базе: {total_keys}")
#
#
# if __name__ == "__main__":
#     provider = DbProvider(conf.db_url)
#     uow = UnitOfWork(session_factory=provider.session_factory, registry=registry)
#     http_client = HttpClient(url=conf.image_api_url)
#     asyncio.run(seed_mass_data(uow=uow, http_client=http_client))

import asyncio
import logging
import random
import string

from adapters.db_provider import DbProvider
from adapters.uow import UnitOfWork
from core import conf
from core.logger import setup_logging
from db.mapper import registry
from domain import Category, Product, ProductItem, ProductVariant, Seller

setup_logging()
log = logging.getLogger(__name__)

NUM_CATEGORIES = 10
PRODUCTS_PER_CAT = 3
VARIANTS_PER_PRODUCT = (1, 3)
KEYS_PER_VARIANT = (5, 20)

# Сгенерируем немного осмысленных слов для теста поиска
SEARCH_KEYWORDS = [
    "Steam",
    "Epic",
    "Global",
    "RU",
    "Premium",
    "Gold",
    "Edition",
    "Key",
    "Account",
    "Gift",
]


def generate_random_key():
    return "-".join(
        "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        for _ in range(3)
    )


async def seed_mass_data(uow):
    log.info(f"🚀 Запуск быстрой генерации данных (БЕЗ картинок)...")

    log.info("👤 Проверка/создание тестового продавца...")
    async with uow:
        seller = await uow.db.read_one(Seller, username="seller1")
        if not seller:
            seller = Seller(username="seller1", password="password")
            seller = await uow.db.create(seller)
            log.info(f"✅ Продавец с ID={seller.id} успешно создан!")

    created_categories = []
    for c in range(1, NUM_CATEGORIES + 1):
        async with uow:
            cat = Category(
                name=f"Категория {c}",
                logo_url="media/dummy_category.png",  # Просто фейковый путь
            )
            saved_cat = await uow.db.create(cat)
            created_categories.append(saved_cat)
        log.info(f"📁 Создана: {saved_cat.name}")

    total_products = 0
    total_keys = 0

    for cat in created_categories:
        log.info(f"⏳ Заполняем '{cat.name}' товарами ({PRODUCTS_PER_CAT} шт.)...")

        for p in range(1, PRODUCTS_PER_CAT + 1):
            variants = []
            num_variants = random.randint(*VARIANTS_PER_PRODUCT)

            for v in range(1, num_variants + 1):
                num_keys = random.randint(*KEYS_PER_VARIANT)
                items = [
                    ProductItem(content=generate_random_key()) for _ in range(num_keys)
                ]
                total_keys += num_keys

                variants.append(
                    ProductVariant(
                        price=float(random.randint(50, 9990)),
                        attributes={
                            "Издание": f"Вариант {v}",
                            "Регион": random.choice(["Global", "RU/CIS", "EU", "USA"]),
                        },
                        items=items,
                    )
                )

            # Добавляем случайные слова в название, чтобы было интереснее тестировать поиск
            random_keyword = random.choice(SEARCH_KEYWORDS)

            product = Product(
                title=f"{random_keyword} Товар {cat.id}-{p} [Test]",
                description=f"Автоматически сгенерированный товар для тестирования поиска. Содержит тег {random_keyword}.",
                category_id=cat.id,
                seller_id=seller.id,
                variants=variants,
                image_url="media/dummy_product.png",  # Фейковый путь
            )

            # Сохраняем напрямую в базу, МИНУЯ сервисы картинок!
            async with uow:
                await uow.db.create(product)

            total_products += 1

    log.info(f"🎉 ГОТОВО! Успешно создано:")
    log.info(f"   - Категорий: {NUM_CATEGORIES}")
    log.info(f"   - Товаров: {total_products}")
    log.info(f"   - Ключей в базе: {total_keys}")


if __name__ == "__main__":
    provider = DbProvider(conf.db_url)
    uow = UnitOfWork(session_factory=provider.session_factory, registry=registry)
    # Нам больше не нужен http_client!
    asyncio.run(seed_mass_data(uow=uow))
