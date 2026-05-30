import logging

from domain import Product

log = logging.getLogger(__name__)


async def create_product(uow, product: Product):
    pass