from domain import Order

from .tasks import generate_payment_link_task


async def generate_payment_link(order: Order, product_title: str):
    # noinspection PyTypeChecker
    await generate_payment_link_task.kiq(
        order_id=order.id, total_cost=order.total_cost, product_title=product_title
    )
