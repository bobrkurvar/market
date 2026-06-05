from decimal import Decimal
from enum import StrEnum


class UserRole(StrEnum):
    client = "client"
    seller = "seller"
    admin = "admin"


class User:
    def __init__(self, username: str,role: UserRole, user_id: int | None = None, password: str | None = None):
        self.id = user_id
        self.username = username
        self.password = password
        self.role = role

    def _validate(self):
        if self.id is None and self.password is None:
            raise ValueError("Для создания нового пользователя придумайте для него пароль")


class Seller(User):
    def __init__(
        self,
        username: str,
        password: str,
        seller_id: int | None = None,
        rating: Decimal | None = None,
        is_active: bool = True,
    ):
        super().__init__(
            user_id=seller_id,
            username=username,
            password=password,
            role=UserRole.seller,
        )
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
        password: str | None = None,
        client_id: int | None = None,
        is_blocked: bool = False,
    ):
        super().__init__(
            user_id=client_id,
            username=username,
            password=password,
            role=UserRole.client,
        )
        self.is_blocked = is_blocked

    def __repr__(self):
        return f"<Client(username={self.username})>"
