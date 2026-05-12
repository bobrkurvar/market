from enum import StrEnum
from . import Product, Client

class OrderStatuses(StrEnum):
    pending_payments = "pending_payments"
    paid = "paid"


class Order:
    def __init__(self, client: Client, product: Product, order_id: int | None = None):
        self.id = order_id
        self.client = client
        self.product = product
        self.status = OrderStatuses.pending_payments

    def mark_as_paid(self):
        self.status = OrderStatuses.paid

