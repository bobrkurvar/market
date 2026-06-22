from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from api.schemas import CategoryShortOut
from adapters.deps import UowDep, GetUserWsDep
from adapters.ws_manager import chat_manager
from domain import OrderMessage, Order, OrderStatuses, DisputeStatuses, Dispute, DisputeMessage, UserRole
import logging

log = logging.getLogger(__name__)

router = APIRouter(prefix="/ws")

@router.websocket("/search")
async def websocket_search(websocket: WebSocket, uow: UowDep):
    log.debug("Вход в поиск")
    await websocket.accept()
    log.debug("Подключение подтверждено")

    try:
        while True:
            query = await websocket.receive_text()

            if len(query.strip()) < 3:
                await websocket.send_json({"suggestions": []})
                continue

            async with uow:
                categories = await uow.category.search_categories_by_product(
                    query=query
                )

                suggestions = []
                for cat in categories:
                    cat_data = CategoryShortOut.model_validate(cat).model_dump()
                    suggestions.append({
                        "type": "category",
                        "data": cat_data
                    })

                await websocket.send_json({"suggestions": suggestions})
    except WebSocketDisconnect:
        log.debug("search connection closed")
        pass


@router.websocket("/orders/{order_id}/chat")
async def order_chat_endpoint(websocket: WebSocket, user: GetUserWsDep, order_id: int, uow: UowDep):
    async with uow:
        order = await uow.db.read_one(Order, id=order_id)

    if user.id not in [order.buyer_id, order.seller_id]:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Нет доступа к чату")
        return

    if order.status != OrderStatuses.paid:
        log.debug("Order status: %s", order.status)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Чат доступен только после оплаты")
        return

    await chat_manager.connect_to_order(websocket, order_id)

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
        chat_manager.disconnect_from_order(websocket, order_id)



@router.websocket("/disputes/{dispute_id}/chat")
async def dispute_chat_endpoint(
    websocket: WebSocket,
    user: GetUserWsDep,
    dispute_id: int,
    uow: UowDep,
):
    async with uow:
        dispute = await uow.db.read_one(
            Dispute,
            id=dispute_id,
            with_raise=True,
        )

        order = await uow.db.read_one(
            Order,
            id=dispute.order_id,
            with_raise=True,
        )

    if (user.role != UserRole.admin) and (not user.id in {order.buyer_id, order.seller_id}):
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Нет доступа к спору",
        )
        return

    if order.status != OrderStatuses.dispute:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Заказ не находится в споре",
        )
        return

    if dispute.status != DisputeStatuses.open:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Спор уже закрыт",
        )
        return

    await chat_manager.connect_to_dispute(websocket, dispute.id)

    try:
        while True:
            text = await websocket.receive_text()

            if not text.strip():
                continue

            async with uow:
                msg = await uow.db.create(
                    DisputeMessage(
                        dispute_id=dispute.id,
                        sender_id=user.id,
                        text=text,
                    )
                )

            await chat_manager.broadcast_to_dispute(
                dispute.id,
                {
                    "id": msg.id,
                    "sender_id": msg.sender_id,
                    "text": msg.text,
                    "created_at": msg.created_at.isoformat(),
                },
            )

    except WebSocketDisconnect:
        chat_manager.disconnect_from_dispute(websocket, dispute.id)