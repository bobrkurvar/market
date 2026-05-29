from sqlalchemy import inspect

import domain
from db import models

def map_user_to_orm(d_obj: domain.User) -> models.User:
    return models.User(username=d_obj.username, password=d_obj.password, type=d_obj.role)

def map_user_to_domain(orm_obj: models.User) -> domain.User:
    return domain.User(username=orm_obj.username, password=orm_obj.password, user_id=orm_obj.id, role=domain.UserRole(orm_obj.type))

def map_order_to_orm(d_obj: domain.Order) -> models.Order:
    return models.Order(
        client_id=d_obj.client_id,
        product_id=d_obj.product_id,
        payment_link=d_obj.payment_link,
        status_name=str(d_obj.status),
        product_snapshot=d_obj.product_snapshot,
        price=d_obj.price,
        amount=d_obj.amount,
        items=[map_product_item_to_orm(item) for item in d_obj._items] if d_obj._items else []
    )

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
        product_id=orm_obj.product_id,
        payment_link=orm_obj.payment_link,
        status=domain.OrderStatuses(orm_obj.status_name),
        items=items,
        price=orm_obj.price,
        amount=orm_obj.amount,
        product_snapshot=orm_obj.product_snapshot
    )

def map_seller_to_orm(d_obj: domain.Seller) -> models.Seller:
    return models.Seller(id=d_obj.id, username=d_obj.username, password=d_obj.password)


def map_client_to_orm(d_obj: domain.Client) -> models.Client:
    return models.Client(id=d_obj.id, username=d_obj.username, password=d_obj.password)


def map_product_to_orm(d_obj: domain.Product) -> models.Product:
    return models.Product(
        id=d_obj.id,
        seller_id=d_obj.seller_id,
        title=d_obj.title,
        description=d_obj.description,
        price=d_obj.price,
        items = [map_product_item_to_orm(item) for item in d_obj._items] if d_obj._items else []
    )

def map_product_item_to_orm(d_obj: domain.ProductItem) -> models.ProductItem:
    return models.ProductItem(
        id=d_obj.id,
        product_id=d_obj.product_id,
        order_id=d_obj.order_id,
        content=d_obj.content,
        status_name=str(d_obj.status)
    )

def map_seller_to_domain(orm_obj: models.Seller) -> domain.Seller:
    return domain.Seller(
        seller_id=orm_obj.id,
        username=orm_obj.username,
        rating=orm_obj.rating,
        is_active=True,
    )


def map_client_to_domain(orm_obj: models.Client) -> domain.Client:
    return domain.Client(
        client_id=orm_obj.id,
        username=orm_obj.username,
        is_blocked=orm_obj.is_blocked,
    )

def map_product_item_to_domain(orm_obj: models.ProductItem) -> domain.ProductItem:
    return domain.ProductItem(
        content=orm_obj.content,
        product_id=orm_obj.product_id,
        status=domain.ProductItemStatuses(orm_obj.status_name),
        item_id=orm_obj.id,
        order_id=orm_obj.order_id
    )

def map_product_to_domain(orm_obj: models.Product) -> domain.Product:
    items = []
    if "items" not in inspect(orm_obj).unloaded:
        items = [map_product_item_to_domain(item) for item in orm_obj.items]

    return domain.Product(
        product_id=orm_obj.id,
        seller_id=orm_obj.seller_id,
        title=orm_obj.title,
        description=orm_obj.description,
        price=orm_obj.price,
        items=items
        #quantity=calculated_quantity,
    )

def map_order_statuses_to_orm(d_obj: domain.OrderStatuses) -> models.OrderStatuses:
    return models.OrderStatuses(
        name=d_obj.value
    )

def map_product_items_statuses_to_orm(d_obj: domain.ProductItemStatuses) -> models.ProductItemStatuses:
    return models.ProductItemStatuses(
        name=d_obj.value
    )

def map_product_items_statuses_to_domain(orm_obj: models.ProductItemStatuses) -> domain.ProductItemStatuses:
    return models.ProductItemStatuses(
        name=orm_obj.name
    )

def map_order_statuses_to_domain(orm_obj: models.ProductItemStatuses) -> domain.ProductItemStatuses:
    return models.ProductItemStatuses(
        name=orm_obj.name
    )




class MapperRegistry:
    def __init__(self):
        self._models = {}  # domain_cls -> orm_model
        self._to_orm_funcs = {}  # domain_cls -> func
        self._to_domain_funcs = {}  # orm_model -> func (Внимание: ключ - ORM класс!)

    def register(self, domain_cls, orm_model, to_orm, to_domain):
        self._models[domain_cls] = orm_model
        self._to_orm_funcs[domain_cls] = to_orm
        self._to_domain_funcs[orm_model] = to_domain

    def get_model(self, domain_cls):
        return self._models[domain_cls]

    def to_orm(self, domain_obj):
        domain_cls = type(domain_obj)
        func = self._to_orm_funcs.get(domain_cls)
        if not func:
            raise RuntimeError(f"Маппер в ORM не найден для {domain_cls}")
        return func(domain_obj)

    def to_domain(self, orm_obj):
        orm_cls = type(orm_obj)
        func = self._to_domain_funcs.get(orm_cls)
        if not func:
            raise RuntimeError(f"Маппер в Домен не найден для {orm_cls}")
        return func(orm_obj)


registry = MapperRegistry()
registry.register(
    domain.Product,
    models.Product,
    to_orm=map_product_to_orm,
    to_domain=map_product_to_domain,
)
registry.register(
    domain.Client,
    models.Client,
    to_orm=map_client_to_orm,
    to_domain=map_client_to_domain,
)
registry.register(
    domain.Seller,
    models.Seller,
    to_orm=map_seller_to_orm,
    to_domain=map_seller_to_domain
)
registry.register(
    domain.ProductItemStatuses,
    models.ProductItemStatuses,
    to_orm=map_product_items_statuses_to_orm,
    to_domain=map_product_items_statuses_to_domain
)
registry.register(
    domain.OrderStatuses,
    models.OrderStatuses,
    to_orm=map_order_statuses_to_orm,
    to_domain=map_order_statuses_to_domain
)
registry.register(
    domain.ProductItem,
    models.ProductItem,
    to_orm=map_product_item_to_orm,
    to_domain=map_product_item_to_domain
)
registry.register(
    domain.Order,
    models.Order,
    to_orm=map_order_to_orm,
    to_domain=map_order_to_domain
)
registry.register(
    domain.User,
    models.User,
    to_orm=map_user_to_orm,
    to_domain=map_user_to_domain,
)