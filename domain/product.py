# from enum import StrEnum

# class DeliveryType(StrEnum):
#    AUTO = "auto"     # Мгновенная выдача ключа
#    MANUAL = "manual" # Нужно участие продавца (услуга)

from .user import Seller


class Product:
    def __init__(
        self,
        title: str,
        price: float,
        seller: Seller | None = None,
        seller_id: int | None = None,
        product_id: int | None = None,
        description: str = "",
        quantity: int = 0,
    ):
        self.id = product_id
        self.seller = seller
        self.title = title
        self.description = description
        self.price = price
        self.quantity = quantity
        self.seller_id = seller_id

        self._validate()

    def _validate(self):
        """Инварианты: правила, которые не могут быть нарушены никогда."""
        if self.seller_id is None and self.seller is None:
            raise ValueError("Нужно передать либо продавца, либо его id")
        if len(self.title) < 3:
            raise ValueError("Заголовок товара слишком короткий")
        if self.price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if self.quantity < 0:
            raise ValueError("Количество не может быть отрицательным")

    def can_be_sold(self, requested_quantity: int = 1) -> bool:
        return self.quantity >= requested_quantity

    def change_price(self, new_price: int):
        """Безопасное изменение цены."""
        if new_price < 0:
            raise ValueError("Новая цена не может быть отрицательной")
        self.price = new_price

    def decrease_stock(self, amount: int = 1):
        """Уменьшение остатков при покупке."""
        if not self.can_be_sold(amount):
            raise ValueError("Недостаточно товара")
        self.quantity -= amount


    def increase_stock(self, amount: int = 1):
        """Восстановление остатков при отмене."""
        self.quantity += amount

    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title}', q={self.quantity})>"
