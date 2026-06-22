from adapters.uow import UnitOfWork
from domain import Admin
from db.mapper import registry
from adapters.db_provider import DbProvider
from core import conf
import asyncio
from core.logger import setup_logging
import logging
from infra.security import get_hash

log = logging.getLogger(__name__)


async def create_admins(uow: UnitOfWork):
    username, password = "admin", "password"
    hash_password = get_hash(password)
    admin = Admin(username=username, password=hash_password)
    async with uow:
        await uow.db.create(admin)


async def main():
    uow = UnitOfWork(registry=registry, provider=DbProvider(url=conf.db_url))
    await create_admins(uow=uow)


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())