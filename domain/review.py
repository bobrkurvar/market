from datetime import datetime, timezone
from .order import Order
from .product import Product, ProductVariant
from .user import User


class Review:
    def __init__(
        self,
        rating: int,
        order: Order | None = None,
        order_id: int | None = None,
        product: Product | None = None,
        product_id: int | None = None,
        product_variant: ProductVariant | None = None,
        product_variant_id: int | None = None,
        author: User | None = None,
        author_id: int | None = None,
        review_id: int | None = None,
        comment: str | None = None,
        created_at: datetime | None = None,
    ):
        self.id = review_id

        self.order = order
        self.order_id = order.id if order else order_id

        self.product = product
        self.product_id = product.id if product else product_id

        self.product_variant = product_variant
        self.product_variant_id = (
            product_variant.id if product_variant else product_variant_id
        )

        self.author = author
        self.author_id = author.id if author else author_id

        self.rating = rating
        self.comment = comment
        self.created_at = created_at or datetime.now(timezone.utc)

        self._validate()

    def _validate(self):
        if not 0 < self.rating <= 5:
            raise ValueError("Оценка должна быть в пределах от 1 до 5")
        if not self.comment.strip():
            raise ValueError("Текст отзыва не может быть пустым")
        if self.order_id is None:
            raise ValueError(
                "Отзыв не может существовать без заказа "
                "(передайте либо объект order, либо order_id)"
            )
        if self.product_id is None:
            raise ValueError(
                "Отзыв не может существовать без товара "
                "(передайте либо объект product, либо product_id)"
            )
        if self.author_id is None:
            raise ValueError(
                "Отзыв не может существовать без автора "
                "(передайте либо объект author, либо author_id)"
            )
        if self.product_variant_id is None and self.id is None:
            raise ValueError(
                "Новый отзыв не может существовать без варианта товара "
                "(передайте либо объект product_variant, либо product_variant_id)"
            )

    @classmethod
    def from_order(
        cls,
        order: Order,
        author_id: int,
        rating: int,
        comment: str | None = None,
    ) -> "Review":
        if order.id is None:
            raise ValueError("Нельзя оставить отзыв по несохранённому заказу")

        if not order.is_paid():
            raise ValueError(
                "Отзыв можно оставить только по успешной сделке"
            )

        if author_id != order.buyer_id:
            raise ValueError(
                "Отзыв может оставить только покупатель"
            )

        if order.product_variant_id is None:
            raise ValueError(
                "У заказа отсутствует вариант товара для отзыва"
            )

        return cls(
            order_id=order.id,
            product_id=order.product_variant.product_id,
            product_variant_id=order.product_variant.id,
            author_id=author_id,
            rating=rating,
            comment=comment,
        )