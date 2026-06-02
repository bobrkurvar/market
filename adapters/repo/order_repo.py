import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from db.models import Order
from domain import OrderStatuses

log = logging.getLogger(__name__)


class OrderRepository:
    def __init__(self, session, registry):
        self.session = session
        self._registry = registry

    async def get_expired_pending_order_ids(self, minutes_ago: int = 15) -> list[int]:
        expiration_threshold = datetime.now(timezone.utc) - timedelta(
            minutes=minutes_ago
        )

        query = select(Order.id).where(
            Order.status_name == OrderStatuses.pending_payments,
            Order.created_at <= expiration_threshold,
        )

        result = await self.session.execute(query)
        return list(result.scalars())
