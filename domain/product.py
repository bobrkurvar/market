from enum import StrEnum
from collections.abc import Collection
from .user import Seller


class ProductItemStatuses(StrEnum):
    available = "available"
    reserved = "reserved"
    sold = "sold"
    compromised = "compromised"


class ProductItem:
    def __init__(
        self,
        content,
        product_id: int | None = None,
        status: ProductItemStatuses = ProductItemStatuses.available,
        item_id: int | None = None,
        order_id: int | None = None,
    ):
        self.product_id = product_id
        self.status = status
        self.id = item_id
        self.content = content
        self.order_id = order_id

    def reserve(self, order_id: int):
        if self.status != ProductItemStatuses.available:
            raise ValueError(f"Нельзя зарезервировать ключ в статусе {self.status}")
        self.status = ProductItemStatuses.reserved
        self.order_id = order_id

    def release(self):
        if self.status != ProductItemStatuses.reserved:
            return
        self.status = ProductItemStatuses.available
        self.order_id = None

    def confirm_purchase(self):
        if self.status != ProductItemStatuses.reserved:
            raise ValueError(f"Нельзя продать не зарезервированный ключ")
        self.status = ProductItemStatuses.sold

    def compromise(self):
        if self.status != ProductItemStatuses.sold:
            raise ValueError("Можно скомпрометировать только проданный товар")
        self.status = ProductItemStatuses.compromised

    def __repr__(self):
        return f"<ProductItem(id={self.id}, status='{self.status}', order_id={self.order_id})>"


class Product:
    def __init__(
        self,
        title: str,
        price: float,
        items: Collection[ProductItem] | ProductItem = None,
        seller: Seller | None = None,
        seller_id: int | None = None,
        product_id: int | None = None,
        description: str = "",
    ):
        self.id = product_id
        self.seller = seller
        self.title = title
        self.description = description
        self.price = price
        self._items = [items] if isinstance(items, ProductItem) else items

        self.seller_id = seller.id if seller and seller.id else seller_id

        self._validate()

    def _validate(self):
        if self.seller_id is None and self.seller is None:
            raise ValueError(
                "Товар не может существовать без продавца (передайте объект seller или seller_id)"
            )
        if len(self.title) < 3:
            raise ValueError("Заголовок товара слишком короткий")
        if self.price < 0:
            raise ValueError("Цена не может быть отрицательной")


    @property
    def items(self):
        if self._items is None:
            raise ValueError("Товар без товарных позиций")
        return self._items

    def change_price(self, new_price: int):
        if new_price < 0:
            raise ValueError("Новая цена не может быть отрицательной")
        self.price = new_price

    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title}')>"
