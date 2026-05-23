from fastapi import APIRouter, HTTPException
from adapters.deps import UowDep
from domain import Order

router = APIRouter()



@router.get("/orders")
async def get_orders(uow: UowDep):
    async with uow:
        return await uow.db.read(Order)


@router.get("/orders/{order_id}")
async def get_order_details(order_id: int, uow: UowDep):
    async with uow:
        return await uow.db.read_one(Order, order_id=order_id)