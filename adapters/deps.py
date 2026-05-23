from typing import Annotated
from fastapi import Depends, Request

from db.mapper import MapperRegistry
from .uow import UnitOfWork
from .web import GetClientDep, GetSellerDep
#from .message_broker import RedisService


def get_uow(request: Request):
    db_provider = request.app.state.db_provider
    if db_provider is None:
        raise RuntimeError("db connection is not initialized")
    return UnitOfWork(provider=db_provider, registry=MapperRegistry())

# def get_db_manager(request: Request):
#     db_provider = request.app.state.db_provider
#     if db_provider is None:
#         raise RuntimeError("db connection is not initialized")
#     return build_crud(db_provider.session_factory)

# def get_redis(request: Request) -> RedisService:
#     provider = request.app.state.redis
#     if provider is None:
#         raise RuntimeError("Redis connection is not initialized")
#     return RedisService(redis=provider.client)


UowDep = Annotated[UnitOfWork, Depends(get_uow)]
#RedisDep = Annotated[RedisService, Depends(get_redis)]
