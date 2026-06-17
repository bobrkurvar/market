from collections.abc import Collection
from datetime import datetime
from enum import StrEnum

from .product import ProductItem, ProductVariant
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
        product_variant: ProductVariant | None = None,
        product_variant_id: int | None = None,
        status: OrderStatuses = OrderStatuses.pending_payments,
        amount: int = 1,
        items: Collection[ProductItem] | ProductItem = None,
        order_id: int | None = None,
        payment_link: str | None = None,
    ):
        self.product_snapshot = product_snapshot or {}
        self.price = price
        self.id = order_id
        self.client = client
        self.client_id = client.id if client else client_id
        self.product_variant = product_variant
        self.product_variant_id = (
            product_variant.id if product_variant else product_variant_id
        )
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
        if self.product_variant_id is None:
            raise ValueError(
                "Заказ не может существовать без товара (передайте либо существующий объект product, либо product_id)"
            )
        if self._items and self.id is None:
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
        if self.id is None:
            raise ValueError(
                "Нельзя зарезервировать ключи: заказ еще не сохранен (отсутствует ID)"
            )
        new_items = [items] if isinstance(items, ProductItem) else list(items)
        if not new_items:
            return
        self._items = list(self._items) if self._items else []
        for item in new_items:
            item.reserve(self.id)
        self._items += new_items

    @property
    def total_cost(self) -> float:
        return self.price * self.amount

    def is_paid(self):
        return self.status == OrderStatuses.paid

    def is_cancelled(self):
        return self.status == OrderStatuses.cancelled

    def is_pending(self):
        return self.status == OrderStatuses.pending_payments
