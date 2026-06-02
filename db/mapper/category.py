import domain
from db import models
from .registry import registry


def map_category_to_domain(orm_obj: models.Category) -> domain.Category:
    return domain.Category(
        category_id=orm_obj.id,
        name=orm_obj.name,
        parent_id=orm_obj.parent_id
    )


def map_category_to_orm(d_obj: domain.Category) -> models.Category:
    return models.Category(
        name=d_obj.name,
        parent_id=d_obj.parent_id
    )



registry.register(domain.Category, models.Category, to_orm=map_category_to_orm, to_domain=map_category_to_domain)


