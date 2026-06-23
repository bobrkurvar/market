import logging
from typing import Any

from fastapi import APIRouter, Request

from adapters.deps import UowDep
from api.schemas import ProductCatalogListOut, ProductDetailOut, ProductWithStatsOut, ReviewRead
from domain import Product, Review
from services.product import search_and_filter_products, get_products_stats

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
    stats = await get_products_stats(uow=uow, products=products)
    products_schemas = []
    for product in products:
        product_schema = ProductWithStatsOut(product=product, **stats.get(product.id, {}))
        products_schemas.append(product_schema)
    return {"items": products_schemas, "total": count}


@router.get("/{slug}/{product_id}/reviews", response_model=list[ReviewRead])
async def get_products_reviews(uow: UowDep, product_id: int, slug: str, limit: int = 10, offset: int = 0):
    async with uow:
        return await uow.db.read(Review, product_id=product_id, limit=limit, offset=offset )


@router.get("/{slug}/{product_id}", response_model=ProductDetailOut)
async def get_product(uow: UowDep, product_id: int, slug: str):
    async with uow:
        product = await uow.db.read_one(
            Product, id=product_id, loaded=["variants", "seller"], with_raise=True
        )
        for variant in product.variants:
            if not variant.is_active:
                continue
            if variant.stock == -1:
                variant.items_count = await uow.product.count_available_items(variant.id)
            elif variant.stock is not None:
                variant.items_count = variant.stock
            if variant.items_count is not None and variant.items_count <= 0:
                variant.is_active = False
        return product