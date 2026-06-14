import pytest
from services.order import make_order, cancel_unpaid_order
from domain import ProductItem, ProductVariant, Order, ProductItemStatuses
from infra.event_bus import EventBus
import logging

log = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_make_order(uow, saved_client, saved_product):
    target_variant = saved_product.variants[0]
    order = await make_order(uow=uow, client=saved_client, product_variant_id=target_variant.id, event_bus=EventBus())
    async with uow:
        items = await uow.db.read(ProductItem, product_variant_id=target_variant.id)
    assert items
    for item in items:
        assert item.product_variant_id == target_variant.id
    assert order is not None
    assert (order.price, order.total_cost) == (100, 100)
    assert (order.product_snapshot["title"], len(order.items), order.is_pending()) == ("test_product", 1, True)
    assert (order.items[0].status, order.client_id, order.product_variant_id) == ("reserved", saved_client.id, target_variant.id)


@pytest.mark.asyncio
async def test_cancel_unpaid_order(uow, saved_client, saved_product):
    target_variant = saved_product.variants[0]
    order = await make_order(uow=uow, client=saved_client, product_variant_id=target_variant.id, event_bus=EventBus())
    cancelled_order: Order = await cancel_unpaid_order(uow, order.id)
    item = cancelled_order.items[0]
    assert (cancelled_order.is_cancelled(), item.status) == (True, ProductItemStatuses.available)
    assert item.order_id is None
    async with uow:
        item: ProductItem = await uow.db.read_one(ProductItem, id=item.id)
        assert item.status == ProductItemStatuses.available