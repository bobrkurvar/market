from taskiq import Context, TaskiqDepends

from adapters.message_broker import RedisService
from adapters.uow import UnitOfWork
from db.mapper import registry


def get_uow(context: Context = TaskiqDepends()):
    """Зависимость для извлечения DB Manager внутри фоновых задач."""
    db_provider = context.state.db_provider
    if db_provider is None:
        raise RuntimeError("DB connection is not initialized in TaskIQ state")
    return UnitOfWork(registry=registry, provider=db_provider)


def get_task_redis(context: Context = TaskiqDepends()) -> RedisService:
    provider = context.state.redis_provider
    if provider is None:
        raise RuntimeError("Redis is not initialized in TaskIQ state")
    return RedisService(redis=provider.client)


def get_payment_service(context: Context = TaskiqDepends()):
    payment_service = context.state.payment_service

    if payment_service is None:
        raise RuntimeError("Payment service is not initialized in TaskIQ state")

    return payment_service