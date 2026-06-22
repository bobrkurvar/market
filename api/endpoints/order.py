from fastapi import APIRouter

from adapters.deps import UowDep, GetUserDep
from domain import Order
from api.schemas import OrderRead, DisputeCreate

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
        return await uow.order.get_user_order_messages(user_id=user.id, order_id=order_id)


@router.post("/{order_id}/dispute")
async def dispute_order(user: GetUserDep, data: DisputeCreate, order_id: int, uow: UowDep):
    async with uow:
        order: Order = await uow.order.get_users_order(order_id=order_id, user_id=user.id)
        dispute = order.open_dispute(opened_by_id=user.id, reason=data.reason)
        await uow.db.save(order)
        return await uow.db.create(dispute)


@router.get("/{order_id}/dispute")
async def get_order_dispute(user: GetUserDep, order_id: int, uow: UowDep):
    async with uow:
        return await uow.dispute.get_user_dispute(order_id=order_id, user_id=user.id)


@router.get("/{order_id}/dispute/messages")
async def get_disputes_messages(user: GetUserDep, order_id: int, uow: UowDep):
    async with uow:
        return await uow.dispute.get_user_dispute_messages(order_id=order_id, user_id=user.id)