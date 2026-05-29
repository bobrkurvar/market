from typing import Annotated

from fastapi import Depends, Request

from db.mapper import registry
from infra.event_bus import EventBus
from adapters.redis import RedisService

from .uow import UnitOfWork


def get_uow(request: Request):
    db_provider = request.app.state.db_provider
    if db_provider is None:
        raise RuntimeError("db connection is not initialized")
    return UnitOfWork(provider=db_provider, registry=registry)


def get_event_bus(request: Request):
    event_bus = request.app.state.event_bus
    if get_event_bus is None:
        raise RuntimeError("Event bus is not initialized")
    return event_bus


def get_redis(request: Request) -> RedisService:
    provider = request.app.state.redis
    if provider is None:
        raise RuntimeError("Redis connection is not initialized")
    return RedisService(redis=provider.client)


UowDep = Annotated[UnitOfWork, Depends(get_uow)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]
RedisDep = Annotated[RedisService, Depends(get_redis)]
