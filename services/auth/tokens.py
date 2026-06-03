import logging
from datetime import datetime, timedelta, timezone

from domain import (RefreshTokenFamilyExpiredError,
                    RefreshTokenReusedCompromisedError,
                    RefreshTokenRotationRaceConditionError)
from infra.auth import check_refresh_token, data_encode_to_jwt
from infra.security import create_token_family_id, create_token_jti

log = logging.getLogger(__name__)


def create_token(data: dict, expire: datetime, token_type: str):
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": token_type})
    return data_encode_to_jwt(to_encode)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    expires_delta = expires_delta if expires_delta else timedelta(minutes=15)
    expire, data = datetime.now(timezone.utc) + expires_delta, data.copy()
    return create_token(data, expire, "access")


def create_refresh_token(
    data: dict, family_id: str, jti: str, expires_delta: timedelta = None
) -> str:
    expires_delta = expires_delta if expires_delta else timedelta(days=7)
    expire, data = datetime.now(timezone.utc) + expires_delta, data.copy()
    data.update(family_id=family_id, jti=jti)
    return create_token(data, expire, "refresh")

async def delete_redis_keys(redis, jti: str, family_id: str):
    await redis.delete(f"rtfam:{family_id}")
    await redis.delete(f"rt:{jti}")


async def check_rotate(payload: dict, redis):
    jti, family_id = payload["jti"], payload["family_id"]
    if not await redis.exists(f"rtfam:{family_id}"):
        raise RefreshTokenFamilyExpiredError

    if await redis.incr(f"rt:{jti}") != 0:
        await delete_redis_keys(redis, jti, family_id)
        raise RefreshTokenReusedCompromisedError

    if not await redis.exists(f"rtfam:{family_id}"):
        await redis.delete(f"rtfam:{family_id}")
        raise RefreshTokenRotationRaceConditionError

    new_jti = create_token_jti()
    await redis.set(f"rt:{new_jti}", -1, ttl=86400 * 7)
    await redis.expire(f"rtfam:{family_id}", ttl=86400 * 7)

    return new_jti, family_id


async def rotate_refresh_token(refresh_token: str, redis) -> tuple[dict, str, str]:
    sub = check_refresh_token(refresh_token)
    jti, family_id = await check_rotate(sub, redis)
    return sub, jti, family_id


def issue_new_tokens(sub: dict, jti: str, family_id: str) -> dict:
    tokens_data = {k: v for k, v in sub.items() if k not in {"jti", "family_id", "exp", "type"}}
    return {
        "access_token": create_access_token(tokens_data),
        "refresh_token": create_refresh_token(tokens_data, jti=jti, family_id=family_id),
    }


async def create_tokens(redis, **data):
    jti, family_id = create_token_jti(), create_token_family_id()
    await redis.set(f"rtfam:{family_id}", value=1, ttl=86400 * 7)
    await redis.set(f"rt:{jti}", value=-1, ttl=86400 * 7)
    return {
        "access_token": create_access_token(data),
        "refresh_token": create_refresh_token(data, jti=jti, family_id=family_id),
    }




