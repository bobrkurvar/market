from fastapi import APIRouter
from fastapi.responses import JSONResponse

from adapters.deps import UowDep, RedisDep
from services.auth import create_tokens_from_login, create_tokens_from_refresh, user_register
from adapters.web import AuthCookies
from infra.security import verify

from .schemas import UserLogin, RefreshToken, UserRegister

router = APIRouter()


@router.post("/refresh")
async def refresh_tokens(refresh_token: RefreshToken, redis: RedisDep, uow: UowDep):
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