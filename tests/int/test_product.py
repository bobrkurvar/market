# import pytest
# from services.product import create_product
# from domain import Client, Product, Seller, ProductVariant, Category, ProductItem
# import logging
#
# log = logging.getLogger(__name__)
#
# @pytest.mark.asyncio
# async def test_create_product(uow):
#     product_variant = ProductVariant(price=7, items=ProductItem(content="content"))
#     async with uow:
#         category = await uow.db.create(Category(name="name"))
#         client = await uow.db.create(Client(username="client", password="password"))
#         seller = await uow.db.create(Seller(username="seller", password="password"))
#         product = Product(title="title", seller=seller, variants=product_variant, category_id=category.id, image_url="url")
#         file = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
#
#     await create_product(uow=uow, product=product, file=file,)