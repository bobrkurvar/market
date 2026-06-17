import asyncio

from adapters.db_provider import DbProvider
from adapters.uow import UnitOfWork
from core import conf
from db.mapper import registry
from domain import OrderStatuses, ProductItemStatuses


async def seed_data():
    db_provider = DbProvider(conf.db_url)
    uow = UnitOfWork(registry=registry, session_factory=db_provider.session_factory)
    product_statuses = [
        ProductItemStatuses(status.value) for status in ProductItemStatuses
    ]
    order_statuses = [OrderStatuses(status.value) for status in OrderStatuses]
    all_data = product_statuses + order_statuses
    async with uow:
        await uow.db.create(seq_data=all_data)


# async def seed_data():
#     db_provider = DbProvider(conf.db_url)
#     uow = UnitOfWork(registry=registry, session_factory=db_provider.session_factory)
#     for status in ProductItemStatuses:
#         try:
#             async with uow:
#                 uow.db.create(ProductItemStatuses(status))
#         except:
#             pass
#
#     for status in OrderStatuses:
#         try:
#             async with uow:
#                 uow.db.create(ProductItemStatuses(status))
#         except:
#             pass

if __name__ == "__main__":
    asyncio.run(seed_data())
