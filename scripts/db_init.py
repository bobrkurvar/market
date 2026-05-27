from adapters.db_provider import DbProvider
from adapters.uow import UnitOfWork
from db.mapper import registry
from core import conf
from domain import OrderStatuses, ProductItemStatuses
import asyncio


async def seed_data():
    db_provider = DbProvider(conf.db_url)
    uow = UnitOfWork(registry=registry, session_factory=db_provider.session_factory)
    product_statuses = [ProductItemStatuses(status.value) for status in ProductItemStatuses]
    order_statuses = [OrderStatuses(status.value) for status in OrderStatuses]
    all_data = product_statuses  + order_statuses
    async with uow:
        await uow.db.create(seq_data=all_data)

if __name__ == "__main__":
    asyncio.run(seed_data())
