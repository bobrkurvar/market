from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from adapters.deps import UowDep, GetUserWsDep
from adapters.ws_manager import chat_manager
from domain import Order, OrderMessage

router = APIRouter(prefix="/orders")


# @router.get("")
# async def get_orders(uow: UowDep):
#     async with uow:
#         return await uow.db.read(Order)
#
#
@router.get("/{order_id}")
async def get_order_details(order_id: int, uow: UowDep):
    async with uow:
        return await uow.db.read_one(Order, id=order_id)


@router.get("/{order_id}/messages")
async def get_chat_history(order_id: int, uow: UowDep):
    async with uow:
        return await uow.db.read(OrderMessage, order_id=order_id, order_by="created_at")


@router.websocket("/ws/{order_id}/chat")
async def order_chat_endpoint(websocket: WebSocket, user: GetUserWsDep, order_id: int, uow: UowDep):
    await chat_manager.connect(websocket, order_id)

    try:
        while True:
            data = await websocket.receive_text()
            async with uow:
                msg = await uow.db.create(
                    OrderMessage(
                        order_id=order_id,
                        sender_id=user.id,
                        text=data,
                    )
                )

            await chat_manager.broadcast_to_order(order_id, {
                "id": msg.id,
                "sender_id": user.id,
                "text": data,
                "is_system": False,
                "created_at": msg.created_at.isoformat()
            })

    except WebSocketDisconnect:
        chat_manager.disconnect(websocket, order_id)