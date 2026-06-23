import logging

from sqlalchemy import func, select
from db.models import Review

log = logging.getLogger(__name__)


class ReviewRepository:
    def __init__(self, session, registry):
        self.session = session
        self._registry = registry

    async def get_products_stats(
        self,
        product_ids: list[int],
    ) -> dict:
        if not product_ids:
            return {}

        stmt = (
            select(
                Review.product_id,
                func.avg(Review.rating).label("rating"),
                func.count(Review.id).label("review_count"),
            )
            .where(Review.product_id.in_(product_ids))
            .group_by(Review.product_id)
        )

        rows = await self.session.execute(stmt)

        return {
            product_id: {
                "rating": round(float(rating), 1) if rating is not None else None,
                "review_count": review_count,
            }
            for product_id, rating, review_count in rows
        }



