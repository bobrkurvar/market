import logging
from typing import Any

from fastapi import APIRouter, Request

from adapters.deps import UowDep
from api.schemas import ProductCatalogListOut, ProductDetailOut
from domain import Product
from services.product import search_and_filter_products

log = logging.getLogger(__name__)

router = APIRouter(prefix="/products")


@router.get("", response_model=ProductCatalogListOut)
async def get_products(
    uow: UowDep,
    limit: int,
    offset: int,
    request: Request,
    min_price: float | None = None,
    max_price: float | None = None,
    category_id: int | None = None,
    q: str | None = None,
):
    raw_params = dict(request.query_params)
    filters: dict[str, Any] = {}

    for k, v in raw_params.items():
        if k not in ("limit", "offset", "q", "max_price", "min_price", "category_id"):
            if isinstance(v, str) and "," in v:
                filters[k] = v.split(",")
            else:
                filters[k] = v
    products, count = await search_and_filter_products(
        uow=uow,
        min_price=min_price,
        max_price=max_price,
        category_id=category_id,
        q=q,
        limit=limit,
        offset=offset,
        **filters
    )
    return {"items": products, "total": count}


@router.get("/{slug}/{product_id}", response_model=ProductDetailOut)
async def get_catalog(uow: UowDep, product_id: int, slug: str):
    async with uow:
        return await uow.db.read_one(
            Product, id=product_id, loaded=["variants", "seller"], with_raise=True
        )
