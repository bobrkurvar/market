from sqlalchemy import inspect
import domain
from db import models
from .product import map_product_to_domain, map_product_variant_to_domain
from .order import map_order_to_domain
from .user import map_user_to_domain
from .registry import registry


def map_review_to_domain(orm_obj: models.Review) -> domain.Review:
    insp = inspect(orm_obj)

    order = None
    if "order" not in insp.unloaded and orm_obj.order:
        order = map_order_to_domain(orm_obj.order)

    product = None
    if "product" not in insp.unloaded and orm_obj.product:
        product = map_product_to_domain(orm_obj.product)

    author = None
    if "author" not in insp.unloaded and orm_obj.author:
        author = map_user_to_domain(orm_obj.author)

    product_variant = None
    if "product_variant" not in insp.unloaded and orm_obj.product_variant:
        product_variant = map_product_variant_to_domain(orm_obj.product_variant)

    return domain.Review(
        review_id=orm_obj.id,
        order_id=orm_obj.order_id,
        product_id=orm_obj.product_id,
        product_variant_id=orm_obj.product_variant_id,
        rating=orm_obj.rating,
        comment=orm_obj.comment,
        created_at=orm_obj.created_at,
        order=order,
        product=product,
        product_variant=product_variant,
        author_id=orm_obj.author_id,
        author=author
    )


def map_review_to_orm(d_obj: domain.Review) -> models.Review:
    return models.Review(
        id=d_obj.id,
        order_id=d_obj.order_id,
        product_id=d_obj.product_id,
        product_variant_id=d_obj.product_variant_id,
        rating=d_obj.rating,
        comment=d_obj.comment,
        created_at=d_obj.created_at,
        author_id=d_obj.author_id
    )

registry.register(domain.Review, models.Review, to_orm=map_review_to_orm, to_domain=map_review_to_domain)