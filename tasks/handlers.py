from domain import OrderCreatedEvent

from .tasks import generate_payment_link_task


async def enqueue_generate_payment_link(event: OrderCreatedEvent):
    await generate_payment_link_task.kiq(
        order_id=event.order_id,
        total_cost=event.total_cost,
        product_title=event.product_title
    )
