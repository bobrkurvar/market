from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from adapters.deps import UowDep, RedisDep
from adapters.web import GetUserDep
from services.auth import create_tokens_from_login, create_tokens_from_refresh, user_register, delete_redis_keys
from adapters.web import AuthCookies
from infra.security import verify

from .schemas import UserLogin, UserRegister

router = APIRouter()

@router.get("/logout")
async def logout(request: Request, redis: RedisDep):
    cookie_manager = AuthCookies()
    response = JSONResponse(content="success")
    refresh_token = cookie_manager.get_refresh_token(request=request)
    jti, family_id = refresh_token["jti"], refresh_token["family_id"]
    cookie_manager.clear_tokens(response=response)
    await delete_redis_keys(redis=redis, jti=jti, family_id=family_id)
    return response


@router.get("/me")
async def get_user_profile(user: GetUserDep):
    return user

@router.post("/refresh")
async def refresh_tokens(request: Request, redis: RedisDep, uow: UowDep):
    cookie_manager = AuthCookies()
    refresh_token = cookie_manager.get_refresh_token(request=request)
    tokens = await create_tokens_from_refresh(redis=redis, uow=uow, refresh_token=refresh_token.value)
    cookie_manager = AuthCookies()
    response = JSONResponse(content="success")
    cookie_manager.set_tokens(tokens=tokens, response=response)
    return response


@router.post("/login")
async def user_login(user: UserLogin, uow: UowDep, redis: RedisDep):
    tokens, user_data = await create_tokens_from_login(uow, username=user.username, password=user.password, verify=verify, redis=redis)
    cookie_manager = AuthCookies()
    response = JSONResponse(content={"user": user_data})
    cookie_manager.set_tokens(tokens=tokens, response=response)
    return response


@router.post("/register")
async def register(user: UserRegister, uow: UowDep, redis: RedisDep):
    tokens, user_data = await user_register(redis=redis, uow=uow, **user.model_dump())
    cookie_manager = AuthCookies()
    response = JSONResponse(content={"user": user_data})
    cookie_manager.set_tokens(tokens=tokens, response=response)
    return response