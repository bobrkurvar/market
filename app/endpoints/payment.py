import logging

from fastapi import APIRouter, Request

from adapters.deps import UowDep
from services.order import confirm_order_payment

log = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhooks/bank")
async def payment_webhook(request: Request, uow: UowDep):
    # 1. Секьюрити: проверяем IP-адреса или подпись
    # (В ЮKassa можно сверять IP с белым списком или проверять базовую авторизацию)
    # await verify_bank_security(request)

    payload = await request.json()

    event_type = payload.get("event")
    order_id = int(payload["object"]["metadata"]["order_id"])
    log.info("Получен вебхук от банка: %s для заказа #%s", event_type, order_id)
    if event_type == "payment.succeeded":
        await confirm_order_payment(uow=uow, order_id=order_id)

    return {"status": "ok"}
