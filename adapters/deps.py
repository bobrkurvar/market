from typing import Annotated

from fastapi import Depends, Request
from starlette.requests import HTTPConnection
from db.mapper import registry
from infra.event_bus import EventBus
from adapters.redis import RedisService
from adapters.http_client import HttpClient

from .uow import UnitOfWork


def get_uow(request: HTTPConnection):
    db_provider = request.app.state.db_provider
    if db_provider is None:
        raise RuntimeError("db connection is not initialized")
    return UnitOfWork(provider=db_provider, registry=registry)


def get_event_bus(request: HTTPConnection):
    event_bus = request.app.state.event_bus
    if get_event_bus is None:
        raise RuntimeError("Event bus is not initialized")
    return event_bus


def get_redis(request: HTTPConnection) -> RedisService:
    provider = request.app.state.redis
    if provider is None:
        raise RuntimeError("Redis connection is not initialized")
    return RedisService(redis=provider.client)

def get_image_api(request: Request) -> HttpClient:
    client = request.app.state.image_api
    if client is None:
        raise RuntimeError("Image API client is not initialized")
    return client


UowDep = Annotated[UnitOfWork, Depends(get_uow)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]
RedisDep = Annotated[RedisService, Depends(get_redis)]
HttpClientDep = Annotated[HttpClient, Depends(get_image_api)]