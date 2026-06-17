import logging

from domain import RefreshTokenMissingError, UserRole
from infra.auth import check_access_token, get_data_from_token

from .tokens import create_tokens, issue_new_tokens, rotate_refresh_token
from .users import check_role, check_user, create_user

log = logging.getLogger(__name__)


async def create_tokens_from_refresh(refresh_token: str | None, redis, uow):
    if refresh_token is None:
        raise RefreshTokenMissingError
    sub, jti, family_id = await rotate_refresh_token(
        refresh_token=refresh_token, redis=redis
    )
    async with uow:
        await check_role(uow, sub)
    return issue_new_tokens(sub=sub, jti=jti, family_id=family_id)


async def create_tokens_from_login(
    uow, redis, username: str, password: str, verify, **data
):
    log.debug("check user")
    async with uow:
        user = await check_user(uow, verify, username, password)
    log.debug("user approve")
    user_data = dict(sub=str(user.id), role=user.role, username=user.username)
    data.update(user_data)
    tokens = await create_tokens(redis=redis, **data)
    return tokens, user_data


async def user_register(redis, uow, username: str, password: str, role: UserRole):
    user = await create_user(uow=uow, username=username, password=password, role=role)
    user_data = dict(sub=str(user.id), role=user.role, username=user.username)
    tokens = await create_tokens(redis=redis, **user_data)
    return tokens, user_data


async def resolve_session_payload(
    access_token: str | None, refresh_token: str | None, redis, uow
):
    if access_token:
        log.debug("access token exists")
        check_access_token(access_token)
        log.debug("access token approve")
        return get_data_from_token(access_token), None
    else:
        new_tokens = await create_tokens_from_refresh(
            refresh_token=refresh_token, redis=redis, uow=uow
        )
        return get_data_from_token(new_tokens["access_token"]), new_tokens
