import logging

from sqlalchemy import desc, exists, func, or_, and_, select
from sqlalchemy.orm import selectinload

from db.models import Product, ProductItem, ProductVariant
from domain import ProductItemStatuses

# from .query_utils import apply_sold_items_filter

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


    @staticmethod
    def _compile_search_query(stmt, query: str):
        fts_query = func.websearch_to_tsquery("russian", query)
        ts_vector = func.to_tsvector("russian", Product.description)
        fts_match = ts_vector.op("@@")(fts_query)
        fts_rank = func.ts_rank(ts_vector, fts_query)

        trgm_sim = func.similarity(Product.title, query)
        total_rank = (trgm_sim * 0.7) + (fts_rank * 0.3)

        search_condition = or_(fts_match, trgm_sim > 0.15)
        return stmt.where(search_condition).order_by(desc(total_rank))

    async def get_filtered_products(
        self,
        limit: int,
        offset: int,
        q: str | None = None,
        category_id: int | None = None,
        max_price: float | None = None,
        min_price: float | None = None,
        **filters
    ):
        stmt = select(Product)
        if q:
            stmt = self._compile_search_query(stmt, q)

        if category_id:
            stmt = stmt.where(Product.category_id == category_id)

        variant_conditions = [ProductVariant.product_id == Product.id]

        if min_price is not None:
            variant_conditions.append(ProductVariant.price >= min_price)
        if max_price is not None:
            variant_conditions.append(ProductVariant.price <= max_price)

        for key, value in filters.items():
            if not value:
                continue

            if isinstance(value, list):
                variant_conditions.append(
                    ProductVariant.attributes[key].astext.in_(value)
                )
            else:
                variant_conditions.append(
                    ProductVariant.attributes[key].astext == str(value)
                )

        if len(variant_conditions) > 1:
            stmt = stmt.where(
                exists().where(and_(*variant_conditions))
            )

        stmt = stmt.options(selectinload(Product.variants))

        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total_count = await self.session.scalar(count_stmt)

        stmt = stmt.limit(limit).offset(offset)
        result = (await self.session.scalars(stmt)).unique()
        return [self._registry.to_domain(r) for r in result], total_count


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

    # async def search_products(self, query: str, limit: int = 8, offset: int = 0):
    #     fts_query = func.websearch_to_tsquery("russian", query)
    #     ts_vector = func.to_tsvector("russian", Product.description)
    #     fts_match = ts_vector.op("@@")(fts_query)
    #     fts_rank = func.ts_rank(ts_vector, fts_query)
    #
    #     trgm_sim = func.similarity(Product.title, query)
    #     total_rank = (trgm_sim * 0.7) + (fts_rank * 0.3)
    #
    #     search_condition = or_(fts_match, trgm_sim > 0.15)
    #     stmt = (
    #         select(Product)
    #         .options(selectinload(Product.variants))
    #         .where(search_condition)
    #         .order_by(desc(total_rank))
    #         .limit(limit)
    #         .offset(offset)
    #     )
    #     count_stmt = select(func.count(Product.id)).where(search_condition)
    #
    #     result = await self.session.execute(stmt)
    #     count_result = await self.session.execute(count_stmt)
    #     return (
    #         tuple(self._registry.to_domain(p) for p in result.scalars()),
    #         count_result.scalar_one(),
    #     )
