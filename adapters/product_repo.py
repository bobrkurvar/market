import logging

from sqlalchemy import select

from db.models import ProductItem
from domain import ProductItemStatuses

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
