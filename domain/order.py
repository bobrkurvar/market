from collections.abc import Collection
from datetime import datetime, timezone
from enum import StrEnum

from .product import ProductItem, ProductVariant
from .user import User, Seller

class DisputeStatuses(StrEnum):
    open = "open"
    resolved = "resolved"


class Message:
    def __init__(
        self,
        sender_id: int,
        text: str,
        created_at: datetime | None = None,
        message_id: int | None = None
    ):
        self.sender_id = sender_id
        self.text = text
        self.created_at = created_at or datetime.now(timezone.utc)
        self.id = message_id


class Dispute:
    def __init__(
        self,
        order_id: int,
        opened_by_id: int,
        reason: str,
        status: DisputeStatuses = DisputeStatuses.open,
        dispute_id: int | None = None,
        created_at: datetime | None = None,
        resolution: str | None = None,
        resolved_by_id: int | None = None,
        resolved_at: datetime | None = None,
    ):
        self.id = dispute_id
        self.order_id = order_id
        self.opened_by_id = opened_by_id
        self.reason = reason
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)
        self.resolution = resolution
        self.resolved_by_id = resolved_by_id
        self.resolved_at = resolved_at


class DisputeMessage(Message):
    def __init__(
        self,
        sender_id: int,
        dispute_id: int,
        text: str,
        created_at: datetime | None = None,
        message_id: int | None = None
    ):
        super().__init__(sender_id=sender_id, text=text, created_at=created_at, message_id=message_id)
        self.dispute_id = dispute_id


class OrderStatuses(StrEnum):
    pending_payments = "pending_payments"
    paid = "paid"
    cancelled = "canceled"
    dispute = "dispute"


class Order:
    def __init__(
        self,
        price: float,
        product_snapshot: dict | None = None,
        buyer: User | None = None,
        buyer_id: int | None = None,
        seller: Seller | None = None,
        seller_id: int | None = None,
        product_variant: ProductVariant | None = None,
        product_variant_id: int | None = None,
        status: OrderStatuses = OrderStatuses.pending_payments,
        amount: int = 1,
        items: Collection[ProductItem] | ProductItem = None,
        order_id: int | None = None,
        payment_link: str | None = None,
        created_at: datetime | None = None,
    ):
        self.created_at = created_at or datetime.now(timezone.utc)
        self.product_snapshot = product_snapshot or {}
        self.price = price
        self.id = order_id
        self.buyer = buyer
        self.buyer_id = buyer.id if buyer else buyer_id
        self.seller = seller
        self.seller_id = seller.id if seller else seller_id
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
        if self.buyer_id is None and self.buyer is None:
            raise ValueError(
                "Заказ не может существовать без покупателя (передайте либо объект buyer, либо buyer_id)"
            )
        if self.seller_id is None:
            raise ValueError(
                "Заказ не может существовать без продавца (передайте либо объект seller, либо seller_id)"
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
        if not self.is_paid():
            raise ValueError("Ключи можно прочитать только у оплаченного твоара")
        return self._items

    def cancel(self):
        if self.is_paid():
            raise ValueError("Нельзя отменить оплаченный заказ")

        if self.is_disputed():
            raise ValueError("Нельзя отменить заказ, находящийся в споре")

        if self.is_cancelled():
            raise ValueError("Нельзя отменить отменённый заказ")

        if not self.is_pending():
            raise ValueError("Заказ нельзя отменить в текущем статусе")

        if self._items is None:
            self.product_variant.increase(self.amount)
        else:
            for item in self._items:
                item.release()

        self.status = OrderStatuses.cancelled

    def pay(self):
        if self.is_paid():
            raise ValueError("Нельзя оплатить уже оплаченный заказ")

        if self.is_cancelled():
            raise ValueError("Попытка оплатить отменённый заказ")

        if self.is_disputed():
            raise ValueError("Нельзя оплатить заказ, находящийся в споре")

        if not self.is_pending():
            raise ValueError("Заказ нельзя оплатить в текущем статусе")

        if self._items:
            for item in self._items:
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

    def is_disputed(self):
        return self.status == OrderStatuses.dispute

    def open_dispute(self, opened_by_id: int, reason: str) -> Dispute:
        if self.is_disputed():
            raise ValueError("Нельзя начать спор повторно")
        if not self.is_paid():
            raise ValueError("Нельзя начать спор по не оплаченному заказу")
        if opened_by_id not in {self.buyer_id, self.seller_id}:
            raise ValueError("Только участник заказа может открыть спор")
        if not reason.strip():
            raise ValueError("Укажите причину спора")

        self.status = OrderStatuses.dispute

        return Dispute(
            order_id=self.id,
            opened_by_id=opened_by_id,
            reason=reason,
        )


class OrderMessage(Message):
    def __init__(
        self,
        sender_id: int,
        order_id: int,
        text: str,
        created_at: datetime | None = None,
        message_id: int | None = None
    ):
        super().__init__(sender_id=sender_id, text=text, created_at=created_at, message_id=message_id)
        self.order_id = order_id