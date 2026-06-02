from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from adapters.deps import UowDep
from domain import Product, DomainFilter, Category
from api.schemas import ProductCatalogListOut, ProductDetailOut
import logging

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/products", response_model=ProductCatalogListOut)
async def get_catalog(uow: UowDep, limit: int, offset: int, q: str | None = None):
    async with uow:
        domain_filters = []
        if q:
            category = DomainFilter(model=Category, field="name", value=q)
            domain_filters.append(category)
        products = await uow.db.read(Product, loaded="variants", domain_filters = domain_filters, limit=limit, offset=offset)
        count = await uow.db.count(Product)
    return {"items": products, "total": count}


@router.get("/products/{product_id}", response_model=ProductDetailOut)
async def get_catalog(uow: UowDep, product_id: int):
    async with uow:
        return await uow.db.read_one(Product, id=product_id, loaded="variants", with_raise=True)


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
                categories = await uow.product.search_categories_by_product(query=query)

                suggestions = [
                    {
                        "id": category.id,
                        "name": category.name,
                        "type": "category"
                    }
                    for category in categories
                ]

                await websocket.send_json({"suggestions": suggestions})

    except WebSocketDisconnect:
        log.debug("search connection closed")
        pass