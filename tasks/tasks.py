import logging

from taskiq import TaskiqDepends

from domain import Order
from services.category import approve_suggested_category
from services.order import cancel_unpaid_order

from .broker import broker
from .deps import get_payment_service, get_uow, get_task_redis

log = logging.getLogger(__name__)


@broker.task
async def generate_payment_link_task(
    order_id: int,
    total_cost: float,
    product_title: str,
    uow=TaskiqDepends(get_uow),
    payment_service=TaskiqDepends(get_payment_service),
    redis_service=TaskiqDepends(get_task_redis)
):
    payment_link = await payment_service.create_payment_intent(
        order_id=order_id,
        amount=total_cost,
        description=f"Оплата товара: {product_title}",
    )

    async with uow:
        order = await uow.db.read_one(Order, id=order_id, with_for_update=True)
        order.payment_link = payment_link
        await uow.db.save(order)
    channel_name = f"order_payment:{order_id}"
    await redis_service.publish(channel_name, payment_link)


# каждые 15 минут
@broker.task(schedule=[{"cron": "*/15 * * * *"}])
async def sweep_expired_orders_task(uow=TaskiqDepends(get_uow)):
    async with uow:
        expired_order_ids = await uow.order.get_expired_pending_order_ids(
            minutes_ago=15
        )
    for order_id in expired_order_ids:
        await cancel_unpaid_order(uow, order_id=order_id)


@broker.task(schedule=[{"cron": "0 3 * * *"}])
async def check_suggested_categories(uow=TaskiqDepends(get_uow)):
    await approve_suggested_category(uow=uow)
