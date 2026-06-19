import asyncio

from fastapi import APIRouter, Depends, HTTPException

#from adapters.deps import EventBusDep, GetClientDep, UowDep, get_client, RedisDep
from adapters.deps import EventBusDep, UowDep, GetUserDep, RedisDep, get_user
from domain import Order
from services.order import make_order

router = APIRouter(prefix="/client", dependencies=[Depends(get_user)])


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

