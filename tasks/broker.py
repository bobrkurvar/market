from taskiq import TaskiqState
from taskiq_redis import ListQueueBroker
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from adapters.message_broker import RedisProvider

from core import conf

broker = ListQueueBroker("redis://localhost:6379/0")



scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)], # Позволяет задавать расписание прямо в декораторе
)


@broker.on_event("startup")
async def startup_event(state: TaskiqState) -> None:
    # state - это хранилище, доступное всем задачам
    state.redis_provider = await RedisProvider.create(conf.redis_host)


@broker.on_event("shutdown")
async def shutdown_event(state: TaskiqState) -> None:
    await state.db_provider.close()
    await state.redis_provider.close()
