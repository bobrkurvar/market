from enum import StrEnum

from . import Client, Product


class OrderStatuses(StrEnum):
    pending_payments = "pending_payments"
    paid = "paid"
    cancelled = "canceled"


class Order:
    def __init__(
        self,
        client: Client,
        product: Product,
        amount: int = 1,
        order_id: int | None = None,
        payment_link: str | None = None,
    ):
        self._id = order_id
        self.client = client
        self.product = product
        self.status = OrderStatuses.pending_payments
        self.amount = amount
        self.payment_link = payment_link

    def cancel(self):
        if self.is_paid():
            raise ValueError("Заказ уже оплачен")
        self.status = OrderStatuses.cancelled
        self.product.increase_stock(amount=self.amount)

    def pay(self):
        if self.is_paid:
            return
        if self.is_cancelled:
            raise ValueError("Попытка оплатить отмененный заказ")

        self.status = OrderStatuses.paid

    @property
    def total_cost(self) -> float:
        return self.product.price * self.amount

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
