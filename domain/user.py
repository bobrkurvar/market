from decimal import Decimal
from collections.abc import Collection
from .order import Order
from enum import StrEnum

class UserRole(StrEnum):
    CLIENT = "client"
    SELLER = "seller"
    ADMIN = "admin"


class User:
    def __init__(self, user_id: int, username: str, password: str, role: UserRole):
        self.id = user_id
        self.username = username
        self.password = password
        self.role = role


class Seller(User):
    def __init__(
        self,
        username: str,
        password: str,
        seller_id: int | None = None,
        rating: Decimal | None = None,
        is_active: bool = True
    ):
        super().__init__(user_id=seller_id, username=username, password=password, role=UserRole.SELLER)
        self.rating = rating
        self.is_active = is_active
        self._validate()

    def _validate(self):
        if self.rating is not None and not (0 <= self.rating <= 5):
            raise ValueError("Рейтинг должен быть в диапазоне от 0 до 5")

    def __repr__(self):
        return f"<Salesperson(username={self.username}, rating={self.rating})>"


class Client(User):
    def __init__(
        self,
        username: str,
        password: str,
        orders: Collection[Order] | None = None,
        client_id: int | None = None,
        is_blocked: bool = False
    ):
        super().__init__(user_id=client_id, username=username, password=password, role=UserRole.CLIENT)
        self.is_blocked = is_blocked
        self.orders = list(orders) if orders else []


    def __repr__(self):
        return f"<Client(username={self.username})>"