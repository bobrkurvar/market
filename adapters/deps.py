import logging
from typing import Annotated

from fastapi import Depends, Request, Response
from starlette.requests import HTTPConnection

from adapters.http_client import HttpClient
from adapters.redis import RedisService
from db.mapper import registry
from domain import Client, Seller
from infra.event_bus import EventBus
from services.auth import (get_client_from_user, get_seller_from_user,
                           resolve_session_payload)

from .cookies import AuthCookies
from .uow import UnitOfWork

log = logging.getLogger(__name__)


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


async def get_user(
    request: Request,
    response: Response,
    cookies: "authCookiesDep",
    redis: "RedisDep",
    uow: "UowDep",
):
    access_token, refresh_token = cookies.get_access_token(
        request
    ), cookies.get_refresh_token(request)
    payload, new_tokens = await resolve_session_payload(
        access_token=access_token, refresh_token=refresh_token, uow=uow, redis=redis
    )
    if new_tokens:
        cookies.set_tokens(response=response, **new_tokens)
    return payload


async def get_client(payload: "GetUserDep", uow: "UowDep") -> Client:
    return await get_client_from_user(payload, uow)


async def get_seller(payload: "GetUserDep", uow: "UowDep") -> Seller:
    return await get_seller_from_user(payload, uow)


UowDep = Annotated[UnitOfWork, Depends(get_uow)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]
RedisDep = Annotated[RedisService, Depends(get_redis)]
HttpClientDep = Annotated[HttpClient, Depends(get_image_api)]
authCookiesDep = Annotated[AuthCookies, Depends()]
GetUserDep = Annotated[dict, Depends(get_user)]
GetClientDep = Annotated[Client, Depends(get_client)]
GetSellerDep = Annotated[Seller, Depends(get_seller)]
