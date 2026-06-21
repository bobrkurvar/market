from collections.abc import Collection
from enum import StrEnum

from .category import Category
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
        product_variant_id: int | None = None,
        status: ProductItemStatuses = ProductItemStatuses.available,
        item_id: int | None = None,
        order_id: int | None = None,
    ):
        self.product_variant_id = product_variant_id
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


class ProductVariant:
    def __init__(
        self,
        price: float,
        is_active: bool = True,
        product_id: int | None = None,
        product: "Product" = None,
        product_variant_id: int | None = None,
        items: Collection[ProductItem] | ProductItem = None,
        attributes: dict | None = None,
        buyer_message: str | None = None,
        stock: int | None = -1
    ):
        self.product = product
        self.product_id = product.id if product else product_id
        self.price = price
        self.id = product_variant_id
        self._items = [items] if isinstance(items, ProductItem) else items
        self.attributes = attributes
        self.buyer_message = buyer_message
        self.stock = stock
        self.items_count = None
        self.is_active = is_active
        self._validate()

    def _validate(self):
        if self.price < 0:
            raise ValueError("Цена не может быть отрицательной")

    def increase(self, amount: int):
        if amount < 0:
            raise ValueError("amount должен быть больше 0")
        if self.stock is not None:
            self.stock += amount

    @property
    def items(self):
        if self._items is None:
            raise ValueError("Товар без товарных позиций")
        return self._items


    def change_price(self, new_price: int):
        if new_price < 0:
            raise ValueError("Новая цена не может быть отрицательной")
        self.price = new_price


class Product:
    def __init__(
        self,
        title: str,
        image_url: str | None = None,
        seller: Seller | None = None,
        seller_id: int | None = None,
        product_id: int | None = None,
        category_id: int | None = None,
        category: Category | None = None,
        suggested_category: str | None = None,
        variants: Collection[ProductVariant] | ProductVariant | None = None,
        description: str = "",
        #items_count: int | None = None,
        buyer_message: str | None = None
    ):
        self.id = product_id
        self.suggested_category = suggested_category
        self.image_url = image_url
        self.seller = seller
        self.title = title
        self.description = description
        self.seller_id = seller.id if seller else seller_id
        self.category = category
        self.category_id = category.id if category else category_id
        self._variants = None
        if variants is not None:
            self.add_variants(variants)
        #self.items_count = items_count
        self.buyer_message = buyer_message
        self._validate()

    def _validate(self):
        if self.seller_id is None:
            raise ValueError(
                "Товар не может существовать без продавца (передайте объект seller у которого есть id или seller_id)"
            )
        if len(self.title) < 3:
            raise ValueError("Заголовок товара слишком короткий")
        if self.category_id is None:
            raise ValueError(
                "Товар не может существовать без категории (передайте объект category у которой есть id или category_id)"
            )

    @property
    def variants_count(self):
        return len(self.variants)


    @property
    def price(self):
        return self.variants[0].price


    def add_variants(self, variants: Collection[ProductVariant] | ProductVariant):
        new_variants = (
            [variants] if isinstance(variants, ProductVariant) else list(variants)
        )
        self._variants = list(self._variants) if self._variants else []
        self._variants += new_variants

    @property
    def variants(self):
        if self._variants is None:
            raise ValueError("Товар без товарных позиций")
        return self._variants


    def can_locate_in_category(self):
        if self.category:
            return not self.category.is_folder

    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title}')>"
