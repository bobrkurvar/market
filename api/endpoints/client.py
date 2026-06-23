import asyncio

from fastapi import APIRouter, Depends, HTTPException

from adapters.deps import EventBusDep, UowDep, GetUserDep, RedisDep, get_user
from domain import Order, Review
from services.order import make_order
from api.schemas import OrderListRead, ReviewCreate, ReviewRead

router = APIRouter(prefix="/client", dependencies=[Depends(get_user)])


@router.get("/orders", response_model=list[OrderListRead])
async def get_client_orders(user: GetUserDep, uow: UowDep):
    async with uow:
        return await uow.db.read(Order, buyer_id=user.id)



@router.get("/disputes")
async def get_client_disputes(user: GetUserDep, uow: UowDep):
    async with uow:
        return await uow.dispute.get_buyer_disputes(buyer_id=user.id)


@router.post("/orders")
async def checkout(
    user: GetUserDep, product_variant_id: int, uow: UowDep, event_bus: EventBusDep
):
    return await make_order(
        uow=uow,
        product_variant_id=product_variant_id,
        buyer=user,
        event_bus=event_bus,
    )




@router.get("/orders/{order_id}/wait-payment")
async def wait_order_payment_link(
    order_id: int,
    uow: UowDep,
    redis: RedisDep
):
    async with uow:
        order = await uow.db.read_one(Order, id=order_id)
        if order.payment_link:
            return {"payment_link": order.payment_link}

    pubsub = redis.conn.pubsub()
    channel_name = f"order_payment:{order_id}"
    await pubsub.subscribe(channel_name)

    try:
        async with asyncio.timeout(60):
            async for message in pubsub.listen():
                if message["type"] == "message":
                    link = message["data"].decode("utf-8")
                    return {"payment_link": link}

    except TimeoutError:
        raise HTTPException(status_code=408, detail="Время ожидания ответа от платежной системы истекло.")
    finally:
        await pubsub.unsubscribe(channel_name)
        await pubsub.close()


@router.post("/orders/{order_id}/review", response_model=ReviewRead)
async def client_post_review(uow: UowDep, user: GetUserDep, order_id: int, data: ReviewCreate):
    async with uow:
        order: Order = await uow.db.read_one(
            Order,
            id=order_id,
            buyer_id=user.id,
            with_for_update=True,
            with_raise=True,
            loaded=["product_variant", "seller"]
        )
        review = Review.from_order(order, author_id=user.id, **data.model_dump())
        old_count = order.seller.reviews_count
        old_rating = float(order.seller.rating) if order.seller.rating is not None else 0.0
        new_rating = ((old_rating * old_count) + data.rating) / (old_count + 1)
        order.seller.rating = round(new_rating, 1)
        order.seller.reviews_count += 1
        await uow.db.save(order.seller)
        return await uow.db.create(review)