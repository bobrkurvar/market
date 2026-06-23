import logging

from sqlalchemy import select, or_

from db.models import Order, Dispute as DisputeOrm, DisputeMessage
from domain import NotFoundError, Dispute as DisputeDomain

log = logging.getLogger(__name__)


class DisputeRepository:
    def __init__(self, session, registry):
        self.session = session
        self._registry = registry

    async def get_buyer_disputes(self, buyer_id: int):
        query = (
            select(DisputeOrm)
            .join(Order, DisputeOrm.order_id == Order.id)
            .where(Order.buyer_id == buyer_id)
            .order_by(DisputeOrm.created_at.desc())
        )

        orm_objs = await self.session.scalars(query)

        return tuple(
            self._registry.to_domain(dispute)
            for dispute in orm_objs
        )

    async def get_user_dispute(
        self,
        order_id: int,
        user_id: int,
    ) -> DisputeDomain:
        query = (
            select(DisputeOrm)
            .join(Order, DisputeOrm.order_id == Order.id)
            .where(
                DisputeOrm.order_id == order_id,
                or_(
                    Order.buyer_id == user_id,
                    Order.seller_id == user_id,
                ),
            )
        )

        orm_obj = await self.session.scalar(query)

        if not orm_obj:
            raise NotFoundError(
                DisputeOrm.__name__,
                order_id=order_id,
                user_id=user_id,
            )

        return self._registry.to_domain(orm_obj)


    async def get_user_dispute_messages(
        self,
        order_id: int,
        user_id: int,
    ):
        query = (
            select(DisputeMessage)
            .select_from(DisputeOrm)
            .join(
                Order,
                DisputeOrm.order_id == Order.id,
            )
            .outerjoin(
                DisputeMessage,
                DisputeMessage.dispute_id == DisputeOrm.id,
            )
            .where(
                DisputeOrm.order_id == order_id,
                or_(
                    Order.buyer_id == user_id,
                    Order.seller_id == user_id,
                ),
            )
            .order_by(DisputeMessage.created_at)
        )

        rows = (await self.session.scalars(query)).all()
        if not rows:
            raise NotFoundError(
                DisputeOrm.__name__,
                order_id=order_id,
                user_id=user_id,
            )

        return tuple(self._registry.to_domain(r) for r in rows if r is not None)


