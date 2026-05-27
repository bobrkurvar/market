import pytest
from services.order import make_order, cancel_unpaid_order
from domain import Client, Product, Seller, ProductItem, Order, ProductItemStatuses
from infra.event_bus import EventBus

@pytest.mark.asyncio
async def test_make_order(uow):
    async with uow:
        client = await uow.db.create(Client(username="client", password="password"))
        seller = await uow.db.create(Seller(username="seller", password="password"))
        product = await uow.db.create(
            Product(
                title="title",
                price=7,
                seller=seller,
                items=ProductItem(content="content")
            )
        )
    order = await make_order(uow=uow, client=client, product_id=product.id, event_bus=EventBus())
    assert order is not None
    assert order.price == 7
    assert order.total_cost == 7
    assert order.product_snapshot["title"] == "title"
    assert order.is_pending()
    assert len(order.items) == 1
    assert order.items[0].status == "reserved"
    assert order.client_id == client.id
    assert order.product_id == product.id


@pytest.mark.asyncio
async def test_cancel_unpaid_order(uow):
    async with uow:
        client = await uow.db.create(Client(username="client", password="password"))
        seller = await uow.db.create(Seller(username="seller", password="password"))
        product = await uow.db.create(
            Product(
                title="title",
                price=7,
                seller=seller,
                items=ProductItem(content="content")
            )
        )
    order = await make_order(uow=uow, client=client, product_id=product.id, event_bus=EventBus())
    cancelled_order: Order = await cancel_unpaid_order(uow, order.id)
    assert cancelled_order.is_cancelled()
    item = cancelled_order.items[0]
    assert item.status == ProductItemStatuses.available
    assert item.order_id is None
    async with uow:
        item: ProductItem = await uow.db.read_one(ProductItem, id=item.id)
        assert item.status == ProductItemStatuses.available