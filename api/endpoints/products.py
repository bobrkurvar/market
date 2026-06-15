from fastapi import APIRouter

from adapters.deps import UowDep
from domain import Product, DomainFilter, Category
from api.schemas import ProductCatalogListOut, ProductDetailOut
import logging
log = logging.getLogger(__name__)

router = APIRouter(prefix="/products")



# @router.get("", response_model=ProductCatalogListOut)
# async def get_catalog(uow: UowDep, limit: int, offset: int, q: str | None = None):
#     async with uow:
#         domain_filters = []
#         if q:
#             category = DomainFilter(model=Category, field="name", value=q)
#             domain_filters.append(category)
#         products = await uow.db.read(Product, loaded="variants", domain_filters=domain_filters, limit=limit, offset=offset)
#         count = await uow.db.count(Product, domain_filters=domain_filters)
#     return {"items": products, "total": count}


@router.get("", response_model=ProductCatalogListOut)
async def get_products(uow: UowDep, limit: int, offset: int, category_id: int | None = None, q: str | None = None):
    async with uow:
        if q:
            products, count = await uow.product.search_products(query=q, limit=limit, offset=offset)
        else:
            filters = {}
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

