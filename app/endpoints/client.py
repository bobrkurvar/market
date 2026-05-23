from fastapi import APIRouter, Depends, HTTPException
from services.order import make_order
from adapters.deps import UowDep, GetClientDep

router = APIRouter()


@router.post("/order")
async def checkout(client: GetClientDep, product_id: int, uow: UowDep):
    await make_order(uow=uow, product_id=product_id, client=client, payment_service=None)


# @router.get("/orders")
# async def checkout(client: GetClientDep, product_id: int, uow: UowDep):
#     await make_order(uow=uow, product_id=product_id, client=client, payment_service=None)