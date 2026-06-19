from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.schemas import CategoryShortOut
from adapters.deps import UowDep, GetUserWsDep
from adapters.ws_manager import chat_manager
from domain import OrderMessage
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