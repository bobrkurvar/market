from taskiq import TaskiqScheduler, TaskiqState, TaskiqEvents
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker

from adapters.message_broker import RedisProvider
from adapters.db_provider import DbProvider
from adapters.payment import FakePaymentService
from core import conf

broker = ListQueueBroker(conf.redis_url)


scheduler = TaskiqScheduler(
    broker=broker,
    sources=[
        LabelScheduleSource(broker)
    ],  # Позволяет задавать расписание прямо в декораторе
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup_event(state: TaskiqState) -> None:
    state.redis_provider = await RedisProvider.create(conf.redis_host)
    state.db_provider = DbProvider(conf.db_url)
    state.payment_service = FakePaymentService()
    # state.payment_service = PaymentService(
    #     shop_id=conf.yookassa_shop_id,
    #     secret_key=conf.yookassa_secret_key,
    # )



@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown_event(state: TaskiqState) -> None:
    await state.db_provider.close()
    await state.redis_provider.close()

from . import tasks
