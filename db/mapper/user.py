from sqlalchemy import inspect

import domain
from db import models

from .registry import registry


def map_user_to_domain(orm_obj: models.User) -> domain.User:
    return domain.User(
        username=orm_obj.username,
        password=orm_obj.password,
        user_id=orm_obj.id,
        role=domain.UserRole(orm_obj.type),
    )


def map_user_to_orm(d_obj: domain.User) -> models.User:
    return models.User(
        username=d_obj.username, password=d_obj.password, type=d_obj.role
    )


def map_seller_to_domain(orm_obj: models.Seller) -> domain.Seller:
    rating = None
    if "rating" not in inspect(orm_obj).unloaded:
        rating = orm_obj.rating
    return domain.Seller(
        seller_id=orm_obj.id,
        username=orm_obj.username,
        rating=rating,
        password=orm_obj.password,
    )


def map_seller_to_orm(d_obj: domain.Seller) -> models.Seller:
    return models.Seller(id=d_obj.id, username=d_obj.username, password=d_obj.password)


# def map_client_to_domain(orm_obj: models.Client) -> domain.Client:
#     is_blocked = None
#     if "is_blocked" not in inspect(orm_obj).unloaded:
#         is_blocked = orm_obj.is_blocked
#     return domain.Client(
#         client_id=orm_obj.id,
#         username=orm_obj.username,
#         is_blocked=is_blocked,
#         password=orm_obj.password,
#     )
#
#
# def map_client_to_orm(d_obj: domain.Client) -> models.Client:
#     return models.Client(id=d_obj.id, username=d_obj.username, password=d_obj.password)


# registry.register(
#     domain.Client,
#     models.Client,
#     to_orm=map_client_to_orm,
#     to_domain=map_client_to_domain,
# )
registry.register(
    domain.Seller,
    models.Seller,
    to_orm=map_seller_to_orm,
    to_domain=map_seller_to_domain,
)
registry.register(
    domain.User,
    models.User,
    to_orm=map_user_to_orm,
    to_domain=map_user_to_domain,
)
