import logging

from adapters.db_provider import DbProvider
from adapters.generic_repo import GenericRepository
from adapters.order_repo import OrderRepository

log = logging.getLogger(__name__)


class UnitOfWork:
    def __init__(self, registry, provider: DbProvider = None, session_factory=None):
        if provider is None and session_factory is None:
            raise ValueError(
                "Должен бы передан либо DbProvider, либо непосредственно session factory"
            )
        self._registry = registry
        self._session_factory = (
            session_factory if session_factory else provider.session_factory
        )

    async def __aenter__(self):
        self.session_ctx = self._session_factory.begin()
        self.session = await self.session_ctx.__aenter__()

        self.db = GenericRepository(session=self.session, registry=self._registry)
        self.order = OrderRepository(session=self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                log.warning("Транзакция откатывается из-за ошибки: %s", exc_val)
        finally:
            await self.session_ctx.__aexit__(exc_type, exc_val, exc_tb)
            self.session = None
            self.db = None

    async def commit(self):
        await self.session.commit()

    async def flush(self):
        await self.session.flush()
