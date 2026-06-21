from fastapi import APIRouter, HTTPException

from adapters.deps import UowDep, GetUserDep
from domain import OrderMessage, NotFoundError, Order, OrderStatuses
from api.schemas import OrderRead

router = APIRouter(prefix="/orders")


@router.get("/{order_id}", response_model=OrderRead)
async def get_order_details(user: GetUserDep, order_id: int, uow: UowDep):
    async with uow:
        return await uow.order.get_users_order(
            order_id=order_id,
            user_id=user.id
        )


@router.get("/{order_id}/messages")
async def get_chat_history(user: GetUserDep, order_id: int, uow: UowDep):
    async with uow:
        try:
            await uow.order.get_users_order(order_id=order_id, user_id=user.id)
        except NotFoundError:
            raise HTTPException(status_code=404)
        return await uow.db.read(OrderMessage, order_id=order_id, order_by="created_at")


@router.post("/{order_id}/dispute")
async def buyer_dispute_order(user: GetUserDep, order_id: int, uow: UowDep):
    async with uow:
        order = await uow.db.read_one(Order, id=order_id, buyer_id=user.id, with_raise=True)
        order.dispute()
        await uow.db.save(order)