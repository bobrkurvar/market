import logging

import pytest

from domain import Order, ProductItem, ProductItemStatuses, ProductVariant
from infra.event_bus import EventBus
from services.order import cancel_unpaid_order, make_order

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_make_order(uow, saved_user, saved_product):
    target_variant = saved_product.variants[0]
    order = await make_order(
        uow=uow,
        buyer=saved_user,
        product_variant_id=target_variant.id,
        event_bus=EventBus(),
    )
    async with uow:
        items = await uow.db.read(ProductItem, product_variant_id=target_variant.id)
    assert items
    for item in items:
        assert item.product_variant_id == target_variant.id
    assert order is not None
    assert (order.price, order.total_cost) == (100, 100)
    assert (order.product_snapshot["title"], len(order._items), order.is_pending()) == (
        "test_product",
        1,
        True,
    )
    assert (order._items[0].status, order.buyer_id, order.product_variant_id) == (
        "reserved",
        saved_user.id,
        target_variant.id,
    )


@pytest.mark.asyncio
async def test_cancel_unpaid_order(uow, saved_user, saved_product):
    target_variant = saved_product.variants[0]
    order = await make_order(
        uow=uow,
        buyer=saved_user,
        product_variant_id=target_variant.id,
        event_bus=EventBus(),
    )
    cancelled_order: Order = await cancel_unpaid_order(uow, order.id)
    item = cancelled_order._items[0]
    assert (cancelled_order.is_cancelled(), item.status) == (
        True,
        ProductItemStatuses.available,
    )
    assert item.order_id is None
    async with uow:
        item: ProductItem = await uow.db.read_one(ProductItem, id=item.id)
        assert item.status == ProductItemStatuses.available
