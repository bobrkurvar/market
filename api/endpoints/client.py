import asyncio

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from adapters.deps import EventBusDep, GetClientDep, UowDep, get_client
from domain import Order
from services.order import make_order

router = APIRouter(prefix="/client", dependencies=[Depends(get_client)])


@router.post("/order")
async def checkout(
    client: GetClientDep, product_variant_id: int, uow: UowDep, event_bus: EventBusDep
):
    return await make_order(
        uow=uow,
        product_variant_id=product_variant_id,
        client=client,
        event_bus=event_bus,
    )


@router.get("/orders/{order_id}/stream")
async def stream_order_status(order_id: int, uow: UowDep):
    async def event_generator():
        while True:
            async with uow:
                order = await uow.db.read_one(Order, id=order_id)

                if order.payment_link:
                    yield {"event": "payment_ready", "data": order.payment_link}
                    break

                yield {"event": "processing", "data": "Генерируем ссылку в банке..."}

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
