from enum import StrEnum

#class DeliveryType(StrEnum):
#    AUTO = "auto"     # Мгновенная выдача ключа
#    MANUAL = "manual" # Нужно участие продавца (услуга)

class Product:
    def __init__(
        self,
        title: str,
        price: float,
        salesperson_id: int,
        id: int | None = None,
        description: str = "",
        quantity: int = 0,
        #delivery_type: DeliveryType = DeliveryType.AUTO,
        is_active: bool = True
    ):
        self.id = id
        self.salesperson_id = salesperson_id
        self.title = title
        self.description = description
        self.price = price
        self.quantity = quantity
        #self.delivery_type = delivery_type
        #self.is_active = is_active

        self._validate()

    def _validate(self):
        """Инварианты: правила, которые не могут быть нарушены никогда."""
        if len(self.title) < 3:
            raise ValueError("Заголовок товара слишком короткий")
        if self.price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if self.quantity < 0:
            raise ValueError("Количество не может быть отрицательным")


    # def can_be_sold(self, requested_quantity: int = 1) -> bool:
    #     """Проверяет, готов ли товар к сделке."""
    #     return (
    #         self.is_active and
    #         self.quantity >= requested_quantity
    #     )

    def change_price(self, new_price: int):
        """Безопасное изменение цены."""
        if new_price < 0:
            raise ValueError("Новая цена не может быть отрицательной")
        self.price = new_price

    def decrease_stock(self, amount: int = 1):
        """Уменьшение остатков при покупке."""
        #if not self.can_be_sold(amount):
        #    raise ValueError("Недостаточно товара на складе")
        self.quantity -= amount

    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title}', q={self.quantity})>"