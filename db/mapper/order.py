from sqlalchemy import inspect

import domain
from db import models
from .product import map_product_item_to_domain, map_product_item_to_orm
from .user import map_client_to_domain
from .registry import registry


def map_order_to_domain(orm_obj: models.Order) -> domain.Order:
    items = []
    insp = inspect(orm_obj)
    if "items" not in insp.unloaded:
        items = [map_product_item_to_domain(item) for item in orm_obj.items]
    client = None
    if "client" not in insp.unloaded:
        client = map_client_to_domain(orm_obj.client)

    return domain.Order(
        order_id=orm_obj.id,
        client_id=orm_obj.client_id,
        client=client,
        product_variant_id=orm_obj.product_variant_id,
        payment_link=orm_obj.payment_link,
        status=domain.OrderStatuses(orm_obj.status_name),
        items=items,
        price=orm_obj.price,
        amount=orm_obj.amount,
        product_snapshot=orm_obj.product_snapshot
    )

def map_order_to_orm(d_obj: domain.Order) -> models.Order:
    return models.Order(
        client_id=d_obj.client_id,
        product_variant_id=d_obj.product_variant_id,
        payment_link=d_obj.payment_link,
        status_name=str(d_obj.status),
        product_snapshot=d_obj.product_snapshot,
        price=d_obj.price,
        amount=d_obj.amount,
        items=[map_product_item_to_orm(item) for item in d_obj._items] if d_obj._items else []
    )


# def map_order_statuses_to_domain(orm_obj: models.ProductItemStatuses) -> domain.ProductItemStatuses:
#     return models.ProductItemStatuses(
#         name=orm_obj.name
#     )
#
# def map_order_statuses_to_orm(d_obj: domain.OrderStatuses) -> models.OrderStatuses:
#     return models.OrderStatuses(
#         name=d_obj.value
#     )


registry.register(domain.Order, models.Order, to_orm=map_order_to_orm, to_domain=map_order_to_domain)
#registry.register(domain.OrderStatuses, models.OrderStatuses, to_orm=map_order_statuses_to_orm, to_domain=map_order_statuses_to_domain)

