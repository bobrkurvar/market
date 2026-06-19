import logging

from domain import (CredentialsValidateError, MissingRoleError, Seller,
                    User, UserLoginNotFoundError, UserRole)
from infra.security import get_hash

log = logging.getLogger(__name__)


async def check_user(uow, verify, username: str, password: str):
    user = await uow.db.read_one(User, username=username)
    if not user:
        log.debug("user with username: %s not found", username)
        raise UserLoginNotFoundError(username)
    if not verify(password, user.password):
        log.debug("wrong password")
        raise CredentialsValidateError
    return user


async def check_role(uow, token_data: dict):
    if token_data["role"] == UserRole.seller:
        await uow.db.read(
            User, type=token_data["role"], id=int(token_data["sub"]), with_raise=True
        )


async def create_user(uow, username: str, password: str, role: UserRole):
    hash_password = get_hash(password)
    log.debug("user role: %s", role)
    if role == UserRole.seller:
        new_account = Seller(username=username, password=hash_password)
    elif role == UserRole.user:
        new_account = User(username=username, password=hash_password)
    else:
        raise ValueError("Неизвестная роль")
    async with uow:
        return await uow.db.create(new_account)


async def get_user_from_payload(payload: dict, uow) -> User:
    user_id = payload.get("sub")
    async with uow:
        return await uow.db.read_one(User, id=int(user_id), with_raise=True)


async def get_seller_from_payload(payload: dict, uow) -> Seller:
    role = payload.get("role")
    user_id = payload.get("sub")

    if role != "seller":
        raise MissingRoleError(user_id=user_id, role=role)

    async with uow:
        return await uow.db.read_one(Seller, id=int(user_id), with_raise=True)
