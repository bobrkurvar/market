import logging

from domain import Client, Order, OrderCreatedEvent, Product
from infra.event_bus import EventBus

log = logging.getLogger(__name__)


async def make_order(
    uow,
    product_id: int,
    client: Client,
    event_bus: EventBus,
    amount: int = 1,
):
    async with uow:
        product = await uow.db.read_one(Product, id=product_id)

        # Внутри read_available_items лежит подзапрос SKIP LOCKED.
        items = await uow.product.read_available_items(
            product_id=product.id, amount=amount
        )

        if len(items) < amount:
            raise ValueError("Недостаточно товара в наличии")

        order = Order(
            client=client,
            amount=amount,
            price=product.price,
            product_id=product.id,
            product_snapshot={"title": product.title, "description": product.description}
        )
        order = await uow.db.create(order)
        order.reserve_items(items)
        for item in items:
            await uow.db.save(item)

        order.product = product
        event_bus.publish(
            OrderCreatedEvent(
                order_id=order.id,
                total_cost=order.total_cost,
                product_title=product.title,
            )
        )
        return order


async def cancel_unpaid_order(uow, order_id: int):
    async with uow:
        order = await uow.db.read_one(
            Order, id=order_id, loaded=["items"], with_for_update=True
        )
        if not order.is_pending():
            return

        order.cancel()
        await uow.db.save(order)
        return order


async def confirm_order_payment(uow, order_id: int):
    async with uow:
        order = await uow.db.read_one(
            Order, loaded="items", with_raise=True, id=order_id, with_for_update=True
        )
        try:
            order.pay()
        except ValueError as e:
            log.critical(str(e))
            raise
        await uow.db.save(order)
    return order
