from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum


class UserRole(StrEnum):
    user = "user"
    seller = "seller"
    admin = "admin"


class User:
    def __init__(
        self,
        username: str,
        role: UserRole = UserRole.user,
        user_id: int | None = None,
        password: str | None = None,
    ):
        self.id = user_id
        self.username = username
        self.password = password
        self.role = role

    def _validate(self):
        if self.id is None and self.password is None:
            raise ValueError(
                "Для создания нового пользователя придумайте для него пароль"
            )

class Admin(User):
    def __init__(
        self,
        username: str,
        admin_id: int | None = None,
        password: str | None = None,
    ):
        super().__init__(username=username, user_id=admin_id, password=password, role=UserRole.admin)


class Seller(User):
    def __init__(
        self,
        username: str,
        password: str,
        seller_id: int | None = None,
        rating: Decimal | None = None,
        is_active: bool = True,
        reviews_count: int = 0,
        sales_count: int = 0
    ):
        super().__init__(
            user_id=seller_id,
            username=username,
            password=password,
            role=UserRole.seller,
        )
        self.rating = rating
        self.is_active = is_active
        self.reviews_count = reviews_count
        self.sales_count = sales_count
        self._validate()

    def _validate(self):
        if self.rating is not None and not (0 <= self.rating <= 5):
            raise ValueError("Рейтинг должен быть в диапазоне от 0 до 5")

    def __repr__(self):
        return f"<Salesperson(username={self.username}, rating={self.rating})>"

    def add_review(self, rating: Decimal) -> None:
        """Добавляет новую оценку и пересчитывает средний рейтинг продавца."""

        if not 0 <= rating <= 5:
            raise ValueError("Оценка должна быть в диапазоне от 0 до 5")

        old_rating = self.rating or Decimal("0")
        old_count = self.reviews_count
        new_rating = ((old_rating * old_count) + rating) / Decimal(old_count + 1)
        self.rating = new_rating.quantize(
            Decimal("0.1"),
            rounding=ROUND_HALF_UP,
        )
        self.reviews_count = old_count + 1


