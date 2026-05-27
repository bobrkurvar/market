import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from adapters.db_provider import DbProvider
from app.endpoints import main_router
from core import conf
from core.logger import setup_logging
from domain import OrderCreatedEvent
from infra.event_bus import EventBus
from tasks.handlers import generate_payment_link

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_provider = DbProvider(conf.db_url)
    event_bus = EventBus()
    event_bus.subscribe(OrderCreatedEvent, generate_payment_link)
    app.state.event_bus = event_bus

    try:
        yield
    finally:
        await app.state.db_provider.close()


log = logging.getLogger(__name__)
app = FastAPI(lifespan=lifespan)
app.include_router(main_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    log.debug("ТАКОЙ URL НЕ ОБСЛУЖИВАЕТСЯ")
    return RedirectResponse("/", status_code=303)


# app.add_exception_handler(UserLoginNotFoundError, user_login_not_found_error_handler)
# app.add_exception_handler(NotFoundError, not_found_handler)
# app.add_exception_handler(AlreadyExistsError, already_exists_handler)
# app.add_exception_handler(ForeignKeyViolationError, foreign_key_handler)
# app.add_exception_handler(
#     RefreshTokenNotExistsError, invalid_tokens_or_not_exists_handler
# )
# app.add_exception_handler(
#     InvalidRefreshTokenError, invalid_tokens_or_not_exists_handler
# )
# app.add_exception_handler(InvalidAccessTokenError, invalid_tokens_or_not_exists_handler)
# app.add_exception_handler(CredentialsValidateError, invalid_credentials_error_handler)
