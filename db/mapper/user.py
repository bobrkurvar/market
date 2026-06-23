from sqlalchemy import inspect
from sqlalchemy.util.preloaded import orm_base

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
    return domain.Seller(
        seller_id=orm_obj.id,
        username=orm_obj.username,
        rating=orm_obj.rating,
        password=orm_obj.password,
        reviews_count=orm_obj.reviews_count,
        sales_count=orm_obj.sales_count
    )


def map_seller_to_orm(d_obj: domain.Seller) -> models.Seller:
    return models.Seller(
        id=d_obj.id,
        username=d_obj.username,
        password=d_obj.password,
        rating=d_obj.rating,
        reviews_count=d_obj.reviews_count,
        sales_count=d_obj.sales_count
    )


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