from collections.abc import Collection
from enum import StrEnum
from datetime import datetime
from .product import Product, ProductItem
from .user import Client


class OrderStatuses(StrEnum):
    pending_payments = "pending_payments"
    paid = "paid"
    cancelled = "canceled"


class Order:
    def __init__(
        self,
        price: float,
        product_snapshot: dict | None = None,
        client: Client | None = None,
        client_id: int | None = None,
        product: Product | None = None,
        product_id: int | None = None,
        status: OrderStatuses = OrderStatuses.pending_payments,
        amount: int = 1,
        items: Collection[ProductItem] | ProductItem = None,
        order_id: int | None = None,
        payment_link: str | None = None,
    ):
        self.product_snapshot = product_snapshot or {}
        self.price = price
        self._id = order_id
        self.client = client
        self.client_id = client.id if client else client_id
        self.product = product
        self.product_id = product.id if product else product_id
        self.status = status
        self.amount = amount
        self._items = [items] if isinstance(items, ProductItem) else items
        self.payment_link = payment_link
        self._validate()

    def _validate(self):
        if self.client_id is None and self.client is None:
            raise ValueError(
                "Заказ не может существовать без клиента (передайте либо объект client, либо client_id)"
            )
        if self.product_id is None:
            raise ValueError(
                "Заказ не может существовать без товара (передайте либо существующий объект product, либо product_id)"
            )
        if self._items and self._id is None:
            raise ValueError(
                "Нельзя передавать товарные позиции при инициализации нового заказа"
            )

    @property
    def items(self):
        if self._items is None:
            raise ValueError("Заказ не может быть без товарных позиций")
        return self._items

    def cancel(self):
        if self.is_paid():
            raise ValueError("Заказ уже оплачен")

        if not self.items:
            raise ValueError("Заказ без товаров")

        for item in self.items:
            item.release()

        self.status = OrderStatuses.cancelled

    def pay(self):
        if self.is_paid():
            return
        if self.is_cancelled():
            raise ValueError("Попытка оплатить отмененный заказ")

        if not self.items:
            raise ValueError("Заказ без товаров")

        for item in self.items:
            item.confirm_purchase()

        self.status = OrderStatuses.paid

    def reserve_items(self, items: Collection[ProductItem] | ProductItem):
        new_items = [items] if isinstance(items, ProductItem) else list(items)
        self._items = list(self._items) if self._items else []
        for item in new_items:
            item.reserve(self.id)
        self._items += new_items

    @property
    def total_cost(self) -> float:
        return self.price * self.amount

    @property
    def id(self) -> int:
        if self._id is None:
            raise ValueError("Идентификатор не подгружен")
        return self._id

    def is_paid(self):
        return self.status == OrderStatuses.paid

    def is_cancelled(self):
        return self.status == OrderStatuses.cancelled

    def is_pending(self):
        return self.status == OrderStatuses.pending_payments
