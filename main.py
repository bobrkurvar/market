import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from adapters.db_provider import DbProvider
from api.endpoints import main_router
from core import conf
from core.logger import setup_logging
from domain import *
from api.err_handlers import *
from infra.event_bus import EventBus
from tasks.handlers import generate_payment_link
from adapters.redis import RedisProvider
from fastapi.middleware.cors import CORSMiddleware

setup_logging()



@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_provider = DbProvider(conf.db_url)
    event_bus = EventBus()
    event_bus.subscribe(OrderCreatedEvent, generate_payment_link)
    app.state.event_bus = event_bus
    app.state.redis = await RedisProvider.create(conf.redis_host)

    try:
        yield
    finally:
        await app.state.db_provider.close()


log = logging.getLogger(__name__)
app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",  # Твой Nuxt в режиме разработки
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.add_exception_handler(UserLoginNotFoundError, user_login_not_found_error_handler)
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(AlreadyExistsError, already_exists_handler)
app.add_exception_handler(ForeignKeyViolationError, foreign_key_handler)
app.add_exception_handler(UnauthorizedError, invalid_tokens_or_not_exists_handler)
app.add_exception_handler(CredentialsValidateError, invalid_credentials_error_handler)
