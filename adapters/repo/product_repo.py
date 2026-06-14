import logging

from sqlalchemy import select, func, or_, desc
from sqlalchemy.orm import selectinload

from db.models import ProductItem, Product, ProductVariant, Category
from domain import ProductItemStatuses
from .query_utils import apply_sold_items_filter

log = logging.getLogger(__name__)


class ProductRepository:
    def __init__(self, session, registry):
        self.session = session
        self._registry = registry

    async def read_available_items(self, variant_id: int, amount: int):
        query = (
            select(ProductItem)
            .where(
                ProductItem.product_variant_id == variant_id,
                ProductItem.status_name == ProductItemStatuses.available,
            )
            .limit(amount)
            .with_for_update(skip_locked=True)
        )
        result = (await self.session.execute(query)).scalars()
        return tuple(self._registry.to_domain(r) for r in result)


    async def get_popular_products_by_orders(self, limit: int):
        stmt = select(Product)
        stmt = apply_sold_items_filter(stmt, is_outer=True)
        stmt = (
            stmt
            .options(selectinload(Product.variants))
            .group_by(Product.id)
            .order_by(desc(func.count(ProductItem.id)))
            .limit(limit)
        )

        result = (await self.session.execute(stmt)).scalars()
        return tuple(self._registry.to_domain(prod) for prod in result)


    async def read_products_with_variants_and_items(self, seller_id: int):
        items_subq = (
            select(func.count(ProductItem.id))
            .select_from(ProductItem)
            .join(ProductVariant, ProductVariant.id == ProductItem.product_variant_id)
            .where(ProductVariant.product_id == Product.id)
            .scalar_subquery()
            .label("items_available")
        )

        query = (
            select(Product, items_subq)
            .where(Product.seller_id == seller_id)
            .options(selectinload(Product.variants))
        )

        result = await self.session.execute(query)
        unique_result = result.unique()
        domain_products = []
        for product_orm, items_count in unique_result:
            domain_product = self._registry.to_domain(product_orm)
            domain_product.items_count = items_count or 0
            domain_products.append(domain_product)

        return domain_products



