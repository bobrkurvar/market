import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, or_, exists
from sqlalchemy.orm import selectinload

from db.models import Order, Dispute as DisputeOrm, OrderMessage
from domain import OrderStatuses, NotFoundError, Dispute as DisputeDomain

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


    async def get_users_order(
        self,
        order_id: int,
        user_id: int,
    ):
        query = select(Order).where(
            Order.id == order_id,
            or_(
                Order.buyer_id == user_id,
                Order.seller_id == user_id
            )
        ).options(selectinload(Order.items))
        orm_obj = await self.session.scalar(query)
        if not orm_obj:
            raise NotFoundError(Order.__name__, id=order_id, user_id=user_id)
        return self._registry.to_domain(orm_obj)


    async def get_user_order_messages(
        self,
        order_id: int,
        user_id: int,
    ):
        query = (
            select(OrderMessage)
            .select_from(Order)
            .outerjoin(
                OrderMessage,
                OrderMessage.order_id == Order.id,
            )
            .where(
                Order.id == order_id,
                or_(
                    Order.buyer_id == user_id,
                    Order.seller_id == user_id,
                ),
            )
            .order_by(OrderMessage.created_at)
        )

        rows = (await self.session.scalars(query)).all()
        if not rows:
            raise NotFoundError(
                Order.__name__,
                id=order_id,
                user_id=user_id,
            )

        return tuple(self._registry.to_domain(r) for r in rows if r is not None)

