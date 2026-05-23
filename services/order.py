from domain import Product, Client, Order
import logging

log = logging.getLogger(__name__)

async def make_order(
    uow,
    product_id: int,
    client: Client,
    payment_service,
    amount: int = 1,
):
    async with uow:
        product = await uow.db.read_one(Product, product_id=product_id, with_for_update=True)
        product.decrease_stock(amount)
        await uow.db.save(product)
        order = Order(client=client, product=product, amount=amount)
        await uow.db.create(order)

    payment_link = await payment_service.create_payment_intent(
        order_id=order.id,
        amount=order.total_cost,
        description=f"Оплата товара: {product.title}"
    )

    return order, payment_link


async def cancel_unpaid_order(uow, order_id: int):
    async with uow:
        order = await uow.db.read_one(Order, id=order_id, loaded="product", with_for_update=True)
        if not order.is_pending():
            return

        order.cancel()
        order.product.increase_stock(order.amount)

        await uow.save(order)


async def confirm_order_payment(uow, order_id: int):
    async with uow:
        order = await uow.db.read_one(Order, with_raise=True, id=order_id)
        try:
            order.pay()
        except ValueError as e:
            log.critical(str(e))
            raise
        await uow.db.save(order, session=uow.session)
    return order