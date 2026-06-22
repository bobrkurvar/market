import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from adapters.cookies import AuthCookies
from adapters.deps import GetUserDep, RedisDep, UowDep
from api.schemas import UserLogin, UserRegister
from infra.auth import get_data_from_token
from infra.security import verify
from services.auth import (create_tokens_from_login,
                           create_tokens_from_refresh, delete_redis_keys,
                           user_register)

router = APIRouter()
log = logging.getLogger(__name__)


@router.post("/logout")
async def logout(request: Request, redis: RedisDep):
    cookie_manager = AuthCookies()
    response = JSONResponse(content="success")
    refresh_token = cookie_manager.get_refresh_token(request=request)
    if refresh_token:
        refresh_token_data = get_data_from_token(refresh_token)
        jti, family_id = refresh_token_data["jti"], refresh_token_data["family_id"]
        await delete_redis_keys(redis=redis, jti=jti, family_id=family_id)
    cookie_manager.clear_tokens(response=response)
    return response


@router.get("/me")
async def get_user_profile(user: GetUserDep):
    # cookie_manager = AuthCookies()
    # access_token = cookie_manager.get_access_token(request=request)
    # log.debug("access_token: %s", access_token)
    return {"user": user}


@router.post("/refresh")
async def refresh_tokens(request: Request, redis: RedisDep, uow: UowDep):
    cookie_manager = AuthCookies()
    refresh_token = cookie_manager.get_refresh_token(request=request)
    tokens = await create_tokens_from_refresh(
        redis=redis, uow=uow, refresh_token=refresh_token
    )
    cookie_manager = AuthCookies()
    response = JSONResponse(content="success")
    cookie_manager.set_tokens(**tokens, response=response)
    return response


@router.post("/login")
async def user_login(user: UserLogin, uow: UowDep, redis: RedisDep):
    tokens, user_data = await create_tokens_from_login(
        uow, username=user.username, password=user.password, verify=verify, redis=redis
    )
    cookie_manager = AuthCookies()
    response = JSONResponse(content={"user": user_data})
    cookie_manager.set_tokens(**tokens, response=response)
    return response


@router.post("/register")
async def register(user: UserRegister, uow: UowDep, redis: RedisDep):
    tokens, user_data = await user_register(redis=redis, uow=uow, **user.model_dump())
    cookie_manager = AuthCookies()
    response = JSONResponse(content={"user": user_data})
    cookie_manager.set_tokens(**tokens, response=response)
    return response
