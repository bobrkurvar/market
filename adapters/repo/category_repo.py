from sqlalchemy import desc, exists, func, literal, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased

from db.models import Category, Product, ProductItem
from db.models import SuggestedCategory as SuggestedCategoryORM
from domain import SuggestedCategory as SuggestedCategoryDomain

from .query_utils import apply_sold_items_filter


class CategoryRepository:
    def __init__(self, session, registry):
        self.session = session
        self._registry = registry

    # async def get_popular_categories_by_orders(self, limit: int):
    #     stmt = select(Category).outerjoin(Product, Product.category_id == Category.id)
    #     stmt = apply_sold_items_filter(stmt, is_outer=True)
    #     stmt = (
    #         stmt
    #         .group_by(Category.id)
    #         .order_by(desc(func.count(ProductItem.id)))
    #         .limit(limit)
    #     )
    #     result = (await self.session.execute(stmt)).scalars()
    #     return tuple(self._registry.to_domain(cat) for cat in result)

    async def get_leaf_categories(self) -> tuple:
        # Подзапрос: проверяем, существует ли строка, где parent_id равен ID текущей категории
        child_exists = exists().where(Category.parent_id == Category.id)

        # Главный запрос: выбираем категории, для которых НЕ существуют дети (~ означает NOT)
        stmt = select(Category).where(~child_exists)
        result = await self.session.execute(stmt)
        return tuple(self._registry.to_domain(cat) for cat in result.scalars())

    async def get_all_categories_tree_flat(self) -> list[dict]:
        categories = (await self.session.execute(select(Category))).scalars()
        children_map = {}
        for c in categories:
            children_map.setdefault(c.parent_id, []).append(c)

        result = []

        def build_tree(parent_id=None, level=0):
            for cat in sorted(children_map.get(parent_id, []), key=lambda x: x.name):
                result.append(
                    {
                        "id": cat.id,
                        "name": cat.name,
                        "level": level,
                        "has_children": cat.id in children_map,
                        "logo_url": cat.logo_url,
                    }
                )
                build_tree(cat.id, level + 1)

        build_tree()

        return result

    async def search_categories_by_product(self, query: str, limit: int = 10):
        trgm_sim = func.similarity(Product.title, query)
        stmt = (
            select(
                Category,
                func.max(trgm_sim).label("max_rank"),
                func.count(Product.id).label("match_count"),
            )
            .select_from(Category)
            .join(Product, Product.category_id == Category.id)
            .where(trgm_sim > 0.15)
            .group_by(Category.id)
            .order_by(desc("max_rank"), desc("match_count"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        categories = result.scalars()
        return tuple(self._registry.to_domain(cat) for cat in categories)

    async def get_suggested_categories_stats(self, min_products_count: int = 10):
        stmt = (
            select(
                Product.suggested_category,
                func.count(Product.id).label("products_count"),
            )
            .where(Product.suggested_category.is_not(None))
            .group_by(Product.suggested_category)
            .having(func.count(Product.id) >= min_products_count)
            .order_by(desc("products_count"))
        )

        result = await self.session.execute(stmt)
        return tuple(
            SuggestedCategoryDomain(name=category[0], products_count=category[1])
            for category in result
        )

    async def upsert_suggested_categories(
        self, categories: tuple[SuggestedCategoryDomain]
    ):
        if not categories:
            return

        values = [
            {
                "name": cat.name,
                "products_count": cat.products_count,
                "status_name": cat.status,
            }
            for cat in categories
        ]
        stmt = insert(SuggestedCategoryORM).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[SuggestedCategoryORM.name],
            set_={"products_count": stmt.excluded.products_count},
        )
        await self.session.execute(stmt)

    async def get_category_branch(self, category_id: int):
        base_query = (
            select(Category.id, Category.parent_id, literal(0).label("lvl"))
            .where(Category.id == category_id)
            .cte(name="cat_tree", recursive=True)
        )
        parent_cat = aliased(Category)
        recursive_query = select(
            parent_cat.id, parent_cat.parent_id, (base_query.c.lvl + 1).label("lvl")
        ).join(base_query, parent_cat.id == base_query.c.parent_id)
        tree_cte = base_query.union_all(recursive_query)
        stmt = (
            select(Category)
            .join(tree_cte, Category.id == tree_cte.c.id)
            .order_by(tree_cte.c.lvl.desc())
        )
        result = await self.session.execute(stmt)
        return tuple(self._registry.to_domain(cat) for cat in result.scalars())
