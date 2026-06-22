from sqlalchemy import inspect

import domain
from db import models

from .product import map_product_item_to_domain, map_product_item_to_orm
from .registry import registry
from .user import map_user_to_domain, map_seller_to_domain


def map_order_to_domain(orm_obj: models.Order) -> domain.Order:
    items = None
    insp = inspect(orm_obj)
    if "items" not in insp.unloaded:
        items = [map_product_item_to_domain(item) for item in orm_obj.items]
    buyer = None
    if "buyer" not in insp.unloaded:
        buyer = map_user_to_domain(orm_obj.buyer)
    seller = None
    if "seller" not in insp.unloaded:
        seller = map_seller_to_domain(orm_obj.seller)

    return domain.Order(
        created_at=orm_obj.created_at,
        order_id=orm_obj.id,
        buyer_id=orm_obj.buyer_id,
        buyer=buyer,
        seller_id=orm_obj.seller_id,
        seller=seller,
        product_variant_id=orm_obj.product_variant_id,
        payment_link=orm_obj.payment_link,
        status=domain.OrderStatuses(orm_obj.status_name),
        items=items,
        price=orm_obj.price,
        amount=orm_obj.amount,
        product_snapshot=orm_obj.product_snapshot,
    )


def map_order_to_orm(d_obj: domain.Order) -> models.Order:
    orm_obj = models.Order(
        id=d_obj.id,
        created_at=d_obj.created_at,
        buyer_id=d_obj.buyer_id,
        seller_id=d_obj.seller_id,
        product_variant_id=d_obj.product_variant_id,
        payment_link=d_obj.payment_link,
        status_name=str(d_obj.status),
        product_snapshot=d_obj.product_snapshot,
        price=d_obj.price,
        amount=d_obj.amount,
    )
    if d_obj._items is not None:
        orm_obj.items = [
            map_product_item_to_orm(item)
            for item in d_obj._items
        ]
    return orm_obj

def map_order_message_to_domain(orm_obj) -> domain.OrderMessage:
    return domain.OrderMessage(
        sender_id=orm_obj.sender_id,
        message_id=orm_obj.id,
        order_id=orm_obj.order_id,
        text=orm_obj.text,
        created_at=orm_obj.created_at
    )

def map_order_message_to_orm(d_obj) -> models.OrderMessage:
    return models.OrderMessage(
        sender_id=d_obj.sender_id,
        order_id=d_obj.order_id,
        text=d_obj.text,
        created_at=d_obj.created_at
    )

registry.register(
    domain.Order, models.Order, to_orm=map_order_to_orm, to_domain=map_order_to_domain
)
registry.register(domain.OrderMessage, models.OrderMessage, to_orm=map_order_message_to_orm, to_domain=map_order_message_to_domain)
