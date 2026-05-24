from taskiq import TaskiqDepends
from domain import Order
from services.order import cancel_unpaid_order
from .deps import get_uow, get_payment_service
from .broker import broker
import logging

log = logging.getLogger(__name__)

@broker.task
async def cancel_unpaid_order_task(order_id: int, uow=TaskiqDepends(get_uow)):
    await cancel_unpaid_order(uow, order_id=order_id)


@broker.task
async def generate_payment_link_task(
    order_id: int,
    total_cost: float,
    product_title: str,
    uow=TaskiqDepends(get_uow),
    payment_service=TaskiqDepends(get_payment_service)
):
    payment_link = await payment_service.create_payment_intent(
        order_id=order_id,
        amount=total_cost,
        description=f"Оплата товара: {product_title}"
    )

    async with uow:
        order = await uow.db.read_one(Order, id=order_id, with_for_update=True)
        order.payment_link = payment_link
        await uow.db.save(order)


# каждые 15 минут
@broker.task(schedule=[{"cron": "*/15 * * * *"}])
async def sweep_expired_orders_task(uow=TaskiqDepends(get_uow)):
    async with uow:
        expired_order_ids = await uow.order.get_expired_pending_order_ids(minutes_ago=15)
    for order_id in expired_order_ids:
        try:
            await cancel_unpaid_order(uow, order_id=order_id)
        except Exception as e:
            log.error("Не удалось отменить заказ %s: %s", order_id, e)


