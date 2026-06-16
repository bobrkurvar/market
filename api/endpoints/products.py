from fastapi import APIRouter, Request

from adapters.deps import UowDep
from domain import Product, Operation, Operations
from api.schemas import ProductCatalogListOut, ProductDetailOut
import logging
from typing import Any

log = logging.getLogger(__name__)

router = APIRouter(prefix="/products")




@router.get("", response_model=ProductCatalogListOut)
async def get_products(
    uow: UowDep,
    limit: int,
    offset: int,
    request: Request,
    min_price: int | None = None,
    max_price: int | None = None,
    category_id: int | None = None,
    q: str | None = None
):
    raw_params = dict(request.query_params)
    filters: dict[str, Any] = {k: v for k, v in raw_params.items() if k not in ("limit", "offset", "q", "max_price", "min_price")}
    async with uow:
        if q:
            products, count = await uow.product.search_products(query=q, limit=limit, offset=offset)
        else:
            #filters = {}
            if min_price is not None:
                filters.update(price=Operation(value=min_price, op=Operations.gte))
            if max_price is not None:
                filters.update(price=Operation(value=max_price, op=Operations.lte))
            if category_id:
                filters.update(category_id=category_id)

            products = await uow.db.read(
                Product,
                loaded="variants",
                **filters,
                limit=limit,
                offset=offset
            )
            count = await uow.db.count(Product, **filters)

    return {"items": products, "total": count}


@router.get("/{slug}/{product_id}", response_model=ProductDetailOut)
async def get_catalog(uow: UowDep, product_id: int, slug: str):
    async with uow:
        return await uow.db.read_one(Product, id=product_id, loaded="variants", with_raise=True)

