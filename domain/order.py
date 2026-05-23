from enum import StrEnum
from . import Product, Client

class OrderStatuses(StrEnum):
    pending_payments = "pending_payments"
    paid = "paid"
    cancelled = "canceled"


class Order:
    def __init__(self, client: Client, product: Product, amount: int = 1, order_id: int | None = None):
        self.id = order_id
        self.client = client
        self.product = product
        self.status = OrderStatuses.pending_payments
        self.amount = amount

    def cancel(self):
        if self.is_paid():
            raise ValueError("Заказ уже оплачен")
        self.status = OrderStatuses.cancelled

    def pay(self):
        if self.is_paid:
            return
        if self.is_cancelled:
            raise ValueError("Попытка оплатить отмененный заказ")

        self.status = OrderStatuses.paid

    @property
    def total_cost(self):
        return self.product.price * self.amount

    def is_paid(self):
        return self.status == OrderStatuses.paid

    def is_cancelled(self):
        return self.status == OrderStatuses.cancelled

    def is_pending(self):
        return self.status == OrderStatuses.pending_payments
