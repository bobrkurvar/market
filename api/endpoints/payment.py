import logging

from fastapi import APIRouter

from adapters.deps import UowDep
from services.order import confirm_order_payment
from api.schemas import OrderPaymentPayload

log = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhooks/payment")
async def payment_webhook(order: OrderPaymentPayload, uow: UowDep):
    log.debug("Payment for order with id: %s", order.id)
    order = await confirm_order_payment(uow=uow, order_id=order.id)
    log.debug("Status after payment: %s", order.status)

    return {"status": "success", "message": "Оплата успешно проведена"}