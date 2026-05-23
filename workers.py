from taskiq import TaskiqState
from taskiq_redis import ListQueueBroker
from adapters.message_broker import RedisProvider, RedisService
from core import conf
from taskiq import Context, TaskiqDepends
from adapters.generic_repo import build_crud
from services.order import cancel_unpaid_order


broker = ListQueueBroker("redis://localhost:6379/0")

@broker.on_event("startup")
async def startup_event(state: TaskiqState) -> None:
    # state - это хранилище, доступное всем задачам
    state.redis_provider = await RedisProvider.create(conf.redis_host)

@broker.on_event("shutdown")
async def shutdown_event(state: TaskiqState) -> None:
    await state.db_provider.close()
    await state.redis_provider.close()


def get_task_db_manager(context: Context = TaskiqDepends()):
    """Зависимость для извлечения DB Manager внутри фоновых задач."""
    db_provider = context.state.db_provider
    if db_provider is None:
        raise RuntimeError("DB connection is not initialized in TaskIQ state")
    return build_crud(db_provider.session_factory)

def get_task_redis(context: Context = TaskiqDepends()) -> RedisService:
    provider = context.state.redis_provider
    if provider is None:
        raise RuntimeError("Redis is not initialized in TaskIQ state")
    return RedisService(redis=provider.client)


@broker.task
async def cancel_unpaid_order_task(
    order_id: int,
    manager = TaskiqDepends(get_task_db_manager)
):
    await cancel_unpaid_order(manager, order_id=order_id)