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
    return models.User(username=d_obj.username, password=d_obj.password)


def map_admin_to_domain(orm_obj: models.AdminOrm) -> domain.Admin:
    return domain.Admin(
        username=orm_obj.username,
        password=orm_obj.password,
        admin_id=orm_obj.id,
    )


def map_admin_to_orm(d_obj: domain.Admin) -> models.AdminOrm:
    return models.AdminOrm(username=d_obj.username, password=d_obj.password)



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
registry.register(
    domain.Admin,
    models.AdminOrm,
    to_orm=map_admin_to_orm,
    to_domain=map_admin_to_domain,
)