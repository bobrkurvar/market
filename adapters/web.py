import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response

from adapters.deps import RedisDep, UowDep
from core import conf
from domain import Client, Seller
from infra.auth import check_access_token, get_data_from_token
from services.auth import create_tokens_from_refresh

log = logging.getLogger(__name__)


class AuthCookies:
    def __init__(self):
        self.refresh_token_key = "refresh_token"
        self.access_token_key = "access_token"
        self.cookie_secret = not conf.is_test

    def get_refresh_token(self, request: Request):
        return request.cookies.get(self.refresh_token_key)

    def get_access_token(self, request: Request):
        return request.cookies.get(self.access_token_key)

    def clear_tokens(self, response: Response):
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token", path="/admin")

    def set_refresh_token(self, response: Response, value: str):
        ttl = 86400 * 7
        response.set_cookie(
            self.refresh_token_key,
            value,
            httponly=True,
            max_age=ttl,
            samesite="strict",
            secure=self.cookie_secret,
            path="/admin",
        )

    def set_access_token(self, response: Response, value: str):
        ttl = 900
        response.set_cookie(
            self.access_token_key,
            value,
            httponly=True,
            max_age=ttl,
            samesite="strict",
            secure=self.cookie_secret,
        )


authCookiesDep = Annotated[AuthCookies, Depends()]


async def get_user(
    request: Request, response: Response, cookies: authCookiesDep, redis: RedisDep
):
    access_token = cookies.get_access_token(request)
    if access_token:
        log.debug("access token exists")
        check_access_token(access_token)
        log.debug("access token approve")
    else:
        refresh_token = cookies.get_refresh_token(request)
        new_access, new_refresh = await create_tokens_from_refresh(refresh_token, redis)
        cookies.set_access_token(response, new_access)
        cookies.set_refresh_token(response, new_refresh)
        return get_data_from_token(new_access)


GetUserDep = Annotated[dict, Depends(get_user)]


async def get_client(payload: GetUserDep, uow: UowDep) -> Client:
    role = payload.get("role")
    user_id = payload.get("sub")

    if role != "client":
        raise HTTPException(status_code=403, detail="Доступно только клиентам")

    async with uow:
        client = await uow.db.read_one(Client, id=user_id, with_raise=True)
        return client


async def get_seller(payload: GetUserDep, uow: UowDep) -> Seller:
    role = payload.get("role")
    user_id = payload.get("sub")

    if role != "seller":
        raise HTTPException(status_code=403, detail="Доступно только продавцам")

    async with uow:
        seller = await uow.db.read_one(Seller, id=user_id, with_raise=True)
        return seller


GetClientDep = Annotated[Client, Depends(get_client)]
GetSellerDep = Annotated[Seller, Depends(get_seller)]
