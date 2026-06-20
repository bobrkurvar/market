import logging
from typing import Annotated

from fastapi import Depends, Request, Response, WebSocket, WebSocketException, status
from starlette.requests import HTTPConnection

from adapters.http_client import HttpClient
from adapters.redis import RedisService
from db.mapper import registry
from domain import Seller
from infra.event_bus import EventBus
from services.auth import (get_seller_from_user, get_user_from_payload,
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


def get_image_api(request: HTTPConnection) -> HttpClient:
    client = request.app.state.image_api
    if client is None:
        raise RuntimeError("Image API client is not initialized")
    return client


async def _extract_and_validate_payload(
    conn: HTTPConnection,
    cookies: "authCookiesDep",
    redis: "RedisDep",
    uow: "UowDep"
):
    access_token = cookies.get_access_token(conn)
    refresh_token = cookies.get_refresh_token(conn)

    payload, new_tokens = await resolve_session_payload(
        access_token=access_token,
        refresh_token=refresh_token,
        uow=uow,
        redis=redis
    )
    return payload, new_tokens


async def get_user(
    request: Request,
    response: Response,
    cookies: "authCookiesDep",
    redis: "RedisDep",
    uow: "UowDep",
):
    payload, new_tokens = await _extract_and_validate_payload(request, cookies, redis, uow)

    if new_tokens:
        cookies.set_tokens(response=response, **new_tokens)
    return await get_user_from_payload(payload=payload, uow=uow)


async def get_user_ws(
    websocket: WebSocket,
    cookies: "authCookiesDep",
    redis: "RedisDep",
    uow: "UowDep",
):
    log.debug("Зашли в get_user_ws")
    try:
        payload, _ = await _extract_and_validate_payload(websocket, cookies, redis, uow)
        return await get_user_from_payload(payload=payload, uow=uow)
    except Exception as e:
        log.error(f"=== ОШИБКА АВТОРИЗАЦИИ WEBSOCKET ===: {repr(e)}")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)


async def get_seller(user: "GetUserDep", uow: "UowDep") -> Seller:
    return await get_seller_from_user(user=user, uow=uow)


UowDep = Annotated[UnitOfWork, Depends(get_uow)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]
RedisDep = Annotated[RedisService, Depends(get_redis)]
HttpClientDep = Annotated[HttpClient, Depends(get_image_api)]
authCookiesDep = Annotated[AuthCookies, Depends()]
GetUserDep = Annotated[dict, Depends(get_user)]
GetUserWsDep = Annotated[dict, Depends(get_user_ws)]
#GetClientDep = Annotated[Client, Depends(get_client)]
GetSellerDep = Annotated[Seller, Depends(get_seller)]
