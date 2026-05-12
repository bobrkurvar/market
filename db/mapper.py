from db import models
from sqlalchemy import inspect
import domain


def map_salesperson_to_orm(d_obj: domain.Salesperson) -> models.Salesperson:
    return models.Salesperson(
        id=d_obj.id,
        username=d_obj.username
    )


def map_client_to_orm(d_obj: domain.Client) -> models.Client:
    return models.Client(
        id=d_obj.id,
        username=d_obj.username
    )


def map_product_to_orm(d_obj: domain.Product) -> models.Product:
    return models.Product(
        id=d_obj.id,
        salesperson_id=d_obj.salesperson_id,
        title=d_obj.title,
        description=d_obj.description,
        price=d_obj.price
    )



def map_salesperson_to_domain(orm_obj: models.Salesperson) -> domain.Salesperson:
    return domain.Salesperson(
        id=orm_obj.id,
        username=orm_obj.username,
        rating=orm_obj.rating,
        is_active=True
    )


def map_client_to_domain(orm_obj: models.Client) -> domain.Client:
    return domain.Client(
        id=orm_obj.id,
        username=orm_obj.username,
        balance=orm_obj.balance,
        is_blocked=orm_obj.is_blocked
    )


def map_product_to_domain(orm_obj: models.Product) -> domain.Product:
    calculated_quantity = 0 if "stock" in inspect(orm_obj).unloaded else len([unit for unit in orm_obj.stock if not unit.is_sold])
    return domain.Product(
        id=orm_obj.id,
        salesperson_id=orm_obj.salesperson_id,
        title=orm_obj.title,
        description=orm_obj.description,
        price=orm_obj.price,
        quantity=calculated_quantity,
    )


class MapperRegistry:
    def __init__(self):
        self._models = {}          # domain_cls -> orm_model
        self._to_orm_funcs = {}    # domain_cls -> func
        self._to_domain_funcs = {} # orm_model -> func (Внимание: ключ - ORM класс!)

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
    to_domain=map_product_to_domain
)
registry.register(
    domain.Client, 
    models.Client, 
    to_orm=map_client_to_orm, 
    to_domain=map_client_to_domain
)