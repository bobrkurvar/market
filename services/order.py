import logging

from domain import User, Order, OrderCreatedEvent, ProductVariant, OrderAlreadyPaidError, Seller, Review
from decimal import Decimal
from infra.event_bus import EventBus

log = logging.getLogger(__name__)


async def make_order(
    uow,
    product_variant_id: int,
    buyer: User,
    event_bus: EventBus,
    amount: int = 1,
):
    async with uow:
        product_variant = await uow.db.read_one(
            ProductVariant, id=product_variant_id, loaded="product"
        )
        product = product_variant.product
        buyer_message = product_variant.buyer_message or product.buyer_message
        snapshot = {
            "title": product.title,
            "description": product.description,
            "attributes": product_variant.attributes,
            "buyer_message": buyer_message
        }

        order = Order(
            buyer=buyer,
            seller_id=product.seller_id,
            amount=amount,
            price=product_variant.price,
            product_variant_id=product_variant.id,
            product_snapshot=snapshot,
        )
        order = await uow.db.create(order)
        if product_variant.stock == -1:
            # Внутри read_available_items лежит подзапрос SKIP LOCKED.
            # Для проверки наличия после покупки делаем +1
            items = await uow.product.read_available_items(
                variant_id=product_variant_id, amount=amount + 1
            )

            if len(items) < amount:
                raise ValueError("Недостаточно товара в наличии")

            # Если база отдала ровно amount значит ключей больше нет!
            if len(items) == amount:
                product_variant.is_active = False
                await uow.db.save(product_variant)

            # Отрезаем лишний ключ (если он был) и резервируем только нужное количество
            items_to_reserve = items[:amount]
            order.reserve_items(items_to_reserve)
            for item in items_to_reserve:
                await uow.db.save(item)

        else:
            # если stock None значит товар не имеет числового ограничения
            if product_variant.stock is not None:
                if product_variant.stock < amount:
                    raise ValueError("Недостаточно товара в наличии")
                product_variant.stock -= amount
                # Если после покупки остаток стал равен нулю — скрываем вариант
                if product_variant.stock == 0:
                    product_variant.is_active = False
                await uow.db.save(product_variant)

        await event_bus.publish(
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
            Order, id=order_id, loaded=["items", "product_variant"], with_for_update=True
        )
        if not order.is_pending():
            return

        order.cancel()
        await uow.db.save(order)
        return order


async def confirm_order_payment(uow, order_id: int):
    async with uow:
        # order = await uow.db.read_one(
        #     Order, loaded=["items", "seller"], with_raise=True, id=order_id, with_for_update=True
        # )
        order = await uow.db.read_one(
            Order, loaded="items", with_raise=True, id=order_id, with_for_update=True
        )
        # Для блокировки строки продавца
        order.seller = await uow.db.read_one(Seller, id=order.seller_id, with_for_update=True, with_raise=True)
        try:
            order.pay()
            #order.seller.sales_count += 1
        except OrderAlreadyPaidError as e:
            log.critical(str(e))
            raise
        await uow.db.save(order)
    return order


async def create_order_review(
    uow,
    order_id: int,
    author_id: int,
    rating: Decimal,
    comment: str | None = None,
) -> Review:
    async with uow:
        order: Order = await uow.db.read_one(
            Order,
            id=order_id,
            buyer_id=author_id,
            with_for_update=True,
            with_raise=True,
            loaded=["product_variant"],
        )

        # Отдельный запрос к seller что бы заблокировать именно его строку в базе
        seller: Seller = await uow.db.read_one(
            Seller,
            id=order.seller_id,
            with_for_update=True,
            with_raise=True,
        )

        review = Review.from_order(
            order,
            author_id=author_id,
            rating=rating,
            comment=comment,
        )

        seller.add_review(rating)

        await uow.db.create(review)
        await uow.db.save(seller)

        return review