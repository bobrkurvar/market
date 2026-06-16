import domain
from db import models
from .registry import registry
from sqlalchemy import inspect


def map_category_to_domain(orm_obj: models.Category) -> domain.Category:
    insp = inspect(orm_obj)
    # children = None
    # if "children" not in insp.unloaded and orm_obj.children:
    #     children = [map_category_to_domain(item) for item in orm_obj.children]

    parent = None
    if "parent" not in insp.unloaded and orm_obj.parent is not None:
        parent = map_category_to_domain(orm_obj.parent)

    return domain.Category(
        category_id=orm_obj.id,
        name=orm_obj.name,
        parent_id=orm_obj.parent_id,
        logo_url=orm_obj.logo_url,
        is_folder=orm_obj.is_folder,
        #children=children,
        parent=parent,
        filter_config=orm_obj.filter_config
    )


def map_category_to_orm(d_obj: domain.Category) -> models.Category:
    return models.Category(
        name=d_obj.name,
        parent_id=d_obj.parent_id,
        logo_url=d_obj.logo_url,
        is_folder=d_obj.is_folder,
        children=[map_category_to_orm(child) for child in d_obj.children],
        filter_config=d_obj.filter_config
    )


def map_suggested_category_to_domain(orm_obj: models.SuggestedCategory) -> domain.SuggestedCategory:
    return domain.SuggestedCategory(
        name=orm_obj.name,
        status=domain.SuggestionStatus(orm_obj.status_name),
        products_count=orm_obj.products_count
    )


def map_suggested_category_to_orm(d_obj: domain.SuggestedCategory) -> models.SuggestedCategory:
    return models.SuggestedCategory(
        name=d_obj.name,
        status_name=d_obj.status,
        products_count=d_obj.products_count
    )

registry.register(domain.Category, models.Category, to_orm=map_category_to_orm, to_domain=map_category_to_domain)
registry.register(domain.SuggestedCategory, models.SuggestedCategory, to_orm=map_suggested_category_to_orm, to_domain=map_suggested_category_to_domain)

