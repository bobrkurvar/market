from sqlalchemy import select, exists, desc, func
from db.models import Category, Product, ProductItem
from .query_utils import apply_sold_items_filter

class CategoryRepository:
    def __init__(self, session, registry):
        self.session = session
        self._registry = registry

    async def get_popular_categories_by_orders(self, limit: int):
        stmt = select(Category).outerjoin(Product, Product.category_id == Category.id)
        stmt = apply_sold_items_filter(stmt, is_outer=True)
        stmt = (
            stmt
            .group_by(Category.id)
            .order_by(desc(func.count(ProductItem.id)))
            .limit(limit)
        )
        result = (await self.session.execute(stmt)).scalars()
        return tuple(self._registry.to_domain(cat) for cat in result)

    async def get_leaf_categories(self) -> tuple:
        # Подзапрос: проверяем, существует ли строка, где parent_id равен ID текущей категории
        child_exists = exists().where(Category.parent_id == Category.id)

        # Главный запрос: выбираем категории, для которых НЕ существуют дети (~ означает NOT)
        stmt = select(Category).where(~child_exists)
        result = await self.session.execute(stmt)
        return tuple(self._registry.to_domain(cat) for cat in result.scalars())

    async def get_all_categories_tree_flat(self) -> list[dict]:
        # 1. Вытаскиваем все категории одним простейшим запросом
        categories = (await self.session.execute(select(Category))).scalars()

        # 2. Группируем детей по parent_id с помощью обычного словаря (Сложность O(N))
        children_map = {}
        for c in categories:
            children_map.setdefault(c.parent_id, []).append(c)

        result = []

        # 3. Компактная рекурсия для плоского списка
        def build_tree(parent_id=None, level=0):
            # Сортируем только детей текущего уровня и проходимся по ним
            for cat in sorted(children_map.get(parent_id, []), key=lambda x: x.name):
                result.append({
                    "id": cat.id,
                    "name": cat.name,
                    "level": level,
                    "has_children": cat.id in children_map,
                    "logo_url": cat.logo_url,
                })
                build_tree(cat.id, level + 1)

        build_tree()

        return result