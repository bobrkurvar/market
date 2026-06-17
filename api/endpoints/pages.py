import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from adapters.deps import UowDep
from api.schemas import HomePageOut, CategoryShortOut
from domain import Category, Product

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/home", response_model=HomePageOut)
async def get_home_page(uow: UowDep, limit: int = 8):
    async with uow:
        # categories = await uow.category.get_popular_categories_by_orders(6)
        # products = await uow.product.get_popular_products_by_orders(8)
        # categories, products = await asyncio.gather(*(categories_cor, products_cor))
        products = await uow.db.read(Product, limit=limit, loaded="variants")
        categories = await uow.db.read(Category, limit=limit, loaded="parent")
    return {"products": products, "categories": categories}


@router.websocket("/ws/search")
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
