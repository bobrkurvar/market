from sqlalchemy import inspect

import domain
from db import models
from .registry import registry

def map_product_items_statuses_to_domain(orm_obj: models.ProductItemStatuses) -> domain.ProductItemStatuses:
    return models.ProductItemStatuses(
        name=orm_obj.name
    )


def map_product_items_statuses_to_orm(d_obj: domain.ProductItemStatuses) -> models.ProductItemStatuses:
    return models.ProductItemStatuses(
        name=d_obj.value
    )


def map_product_item_to_domain(orm_obj: models.ProductItem) -> domain.ProductItem:
    return domain.ProductItem(
        content=orm_obj.content,
        product_variant_id=orm_obj.product_variant_id,
        status=domain.ProductItemStatuses(orm_obj.status_name),
        item_id=orm_obj.id,
        order_id=orm_obj.order_id
    )

def map_product_item_to_orm(d_obj: domain.ProductItem) -> models.ProductItem:
    return models.ProductItem(
        id=d_obj.id,
        product_variant_id=d_obj.product_variant_id,
        order_id=d_obj.order_id,
        content=d_obj.content,
        status_name=str(d_obj.status)
    )

def map_product_to_domain(orm_obj: models.Product) -> domain.Product:
    insp = inspect(orm_obj)
    variants = []
    if "variants" not in insp.unloaded:
        variants = [map_product_variant_to_domain(variant) for variant in orm_obj.variants]
    category = None
    if "category" not in insp.unloaded:
        category = orm_obj.category

    return domain.Product(
        product_id=orm_obj.id,
        seller_id=orm_obj.seller_id,
        title=orm_obj.title,
        description=orm_obj.description,
        variants=variants,
        category_id=orm_obj.category_id,
        category=category,
        image_url=orm_obj.image_url
    )

def map_product_to_orm(d_obj: domain.Product) -> models.Product:
    return models.Product(
        image_url=d_obj.image_url,
        id=d_obj.id,
        seller_id=d_obj.seller_id,
        title=d_obj.title,
        description=d_obj.description,
        category_id=d_obj.category_id,
        variants = [map_product_variant_to_orm(variant) for variant in d_obj._variants] if d_obj._variants else []
    )


def map_product_variant_to_domain(orm_obj: models.ProductVariant) -> domain.ProductVariant:
    items = []
    if "items" not in inspect(orm_obj).unloaded:
        items = [map_product_item_to_domain(item) for item in orm_obj.items]
    product = None
    if "product" not in inspect(orm_obj).unloaded:
        product = orm_obj.product

    return domain.ProductVariant(
        product_id=orm_obj.product_id,
        product=product,
        price=orm_obj.price,
        attributes=orm_obj.attributes,
        items=items,
        product_variant_id=orm_obj.id
    )


def map_product_variant_to_orm(d_obj: domain.ProductVariant) -> models.ProductVariant:
    return models.ProductVariant(
        product_id=d_obj.product_id,
        price=d_obj.price,
        attributes=d_obj.attributes,
        items=[map_product_item_to_orm(item) for item in d_obj._items] if d_obj._items else []
    )


registry.register(domain.ProductVariant, models.ProductVariant,to_orm=map_product_variant_to_orm, to_domain=map_product_variant_to_domain)
registry.register(domain.ProductItemStatuses, models.ProductItemStatuses, to_orm=map_product_items_statuses_to_orm, to_domain=map_product_items_statuses_to_domain)
registry.register(domain.ProductItem, models.ProductItem, to_orm=map_product_item_to_orm, to_domain=map_product_item_to_domain)
registry.register(domain.Product, models.Product, to_orm=map_product_to_orm, to_domain=map_product_to_domain,)