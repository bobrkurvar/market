from decimal import Decimal

class Salesperson:
    def __init__(
        self,
        username: str,
        id: int | None = None,
        rating: Decimal | None = None,
        is_active: bool = True
    ):
        self.id = id
        self.username = username
        self.rating = rating
        self.is_active = is_active

        self._validate()

    def _validate(self):
        if not self.username:
            raise ValueError("Имя продавца не может быть пустым")
        if self.rating is not None and not (0 <= self.rating <= 5):
            raise ValueError("Рейтинг должен быть в диапазоне от 0 до 5")

    def __repr__(self):
        return f"<Salesperson(username={self.username}, rating={self.rating})>"


class Client:
    def __init__(
        self,
        username: str,
        id: int | None = None,
        balance: float = 0,
        is_blocked: bool = False
    ):
        self.id = id
        self.username = username
        self.balance = balance
        self.is_blocked = is_blocked

        self._validate()

    def _validate(self):
        if not self.username:
            raise ValueError("Имя клиента не может быть пустым")
        if self.balance < 0:
            raise ValueError("Баланс не может быть отрицательным")

    def __repr__(self):
        return f"<Client(username={self.username}, balance={self.balance})>"