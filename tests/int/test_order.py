import pytest
from services.order import make_order, cancel_unpaid_order
from domain import Client, Product, Seller, ProductItem, Order, ProductItemStatuses, ProductVariant, Category
from infra.event_bus import EventBus
import logging

log = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_make_order(uow):
    product_variant = ProductVariant(price=7, items=ProductItem(content="content"))
    async with uow:
        category = await uow.db.create(Category(name="name"))
        client = await uow.db.create(Client(username="client", password="password"))
        seller = await uow.db.create(Seller(username="seller", password="password"))
        product = Product(title="title", seller=seller, variants=product_variant, category_id=category.id, image_url="url")
        product = await uow.db.create(product)
        product = await uow.db.read_one(Product, id=product.id, loaded="variants")
        target_variant = product.variants[0]
    order = await make_order(uow=uow, client=client, product_variant_id=target_variant.id, event_bus=EventBus())
    async with uow:
        items = await uow.db.read(ProductItem, product_variant_id=target_variant.id)
    assert items
    for item in items:
        assert item.product_variant_id == target_variant.id
    assert order is not None
    assert order.price == 7
    assert order.total_cost == 7
    assert order.product_snapshot["title"] == "title"
    assert order.is_pending()
    assert len(order.items) == 1
    assert order.items[0].status == "reserved"
    assert order.client_id == client.id
    assert order.product_variant_id == target_variant.id


@pytest.mark.asyncio
async def test_cancel_unpaid_order(uow):
    product_variant = ProductVariant(price=7, items=ProductItem(content="content"))
    async with uow:
        category = await uow.db.create(Category(name="name"))
        client = await uow.db.create(Client(username="client", password="password"))
        seller = await uow.db.create(Seller(username="seller", password="password"))
        product = Product(title="title", seller=seller, variants=product_variant, category_id=category.id, image_url="url")
        product.add_variants(product_variant)
        product = await uow.db.create(product)
        product = await uow.db.read_one(Product, id=product.id, loaded="variants")
        target_variant = product.variants[0]
    order = await make_order(uow=uow, client=client, product_variant_id=target_variant.id, event_bus=EventBus())
    cancelled_order: Order = await cancel_unpaid_order(uow, order.id)
    assert cancelled_order.is_cancelled()
    item = cancelled_order.items[0]
    assert item.status == ProductItemStatuses.available
    assert item.order_id is None
    async with uow:
        item: ProductItem = await uow.db.read_one(ProductItem, id=item.id)
        assert item.status == ProductItemStatuses.available