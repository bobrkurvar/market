from decimal import Decimal

from sqlalchemy import (DECIMAL, BigInteger, CheckConstraint, ForeignKey,
                        Index, String, Text, UniqueConstraint, func,
                        literal_column, DateTime, Integer)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from domain import OrderStatuses, ProductItemStatuses, SuggestionStatus
from datetime import datetime, timezone

class Base(AsyncAttrs, DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"))
    image_url: Mapped[str]
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    suggested_category: Mapped[str] = mapped_column(String(100), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    activate_instruction: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant",
        cascade="all, delete-orphan",
        back_populates="product",
        passive_deletes=True,
    )
    seller: Mapped["Seller"] = relationship("Seller", back_populates="products")

    __table_args__ = (
        # 1. Полнотекстовый поиск (FTS) по заголовку и описанию (склонения)
        Index(
            "idx_product_fts",
            func.to_tsvector(literal_column("'russian'"), description),
            postgresql_using="gin",
        ),
        # 2. Индекс для Триграмм по заголовку
        Index(
            "idx_product_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )
    price: Mapped[float]
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    activate_instruction: Mapped[str | None] = mapped_column(Text, nullable=True)
    stock: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    items: Mapped[list["ProductItem"]] = relationship(
        "ProductItem",
        cascade="all, delete-orphan",
        back_populates="variant",
        passive_deletes=True,
    )


class ProductItem(Base):
    __tablename__ = "product_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE")
    )
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)

    content: Mapped[str] = mapped_column(Text)
    status_name: Mapped[str]
    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant", back_populates="items"
    )
    __table_args__ = (
        CheckConstraint(
            "status_name IN ({})".format(
                ", ".join(f"'{status}'" for status in ProductItemStatuses)
            ),
            name="check_product_item_status",
        ),
    )


# class ProductItemStatuses(Base):
#     __tablename__ = "product_item_statuses"
#     name: Mapped[str] = mapped_column(primary_key=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "user",
    }

class Seller(User):
    __tablename__ = "sellers"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    rating: Mapped[Decimal | None] = mapped_column(
        DECIMAL(2, 1), server_default=None, default=None, nullable=True
    )
    products: Mapped[list["Product"]] = relationship("Product", back_populates="seller")
    __mapper_args__ = {
        "polymorphic_identity": "seller",  # Значение для колонки users.type
    }

#
# class Client(User):
#     __tablename__ = "clients"
#     id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
#     is_blocked: Mapped[bool] = mapped_column(default=False, server_default="false")
#     # cart: Mapped["Cart"] = relationship("Cart", back_populates="client")
#     __mapper_args__ = {
#         "polymorphic_identity": "client",  # Значение для колонки users.type
#     }


# class Cart(Base):
#     __tablename__ = "cart"
#     client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), primary_key=True)
#     product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
#     quantity: Mapped[int]
#
#     client: Mapped["Client"] = relationship("Client", back_populates="cart")
#     product: Mapped["Product"] = relationship("Product")


# class OrderStatuses(Base):
#     __tablename__ = "order_statuses"
#     name: Mapped[str] = mapped_column(String(20), primary_key=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"))
    product_variant_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_variants.id", ondelete="SET NULL")
    )
    payment_link: Mapped[str | None] = mapped_column(default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    status_name: Mapped[str]
    items: Mapped[list["ProductItem"]] = relationship("ProductItem")
    buyer: Mapped["User"] = relationship("User", foreign_keys=[buyer_id])
    seller: Mapped["Seller"] = relationship("Seller", foreign_keys=[seller_id])
    price: Mapped[float]
    amount: Mapped[int]
    product_snapshot: Mapped[dict] = mapped_column(
        JSONB, default={}, server_default="{}"
    )
    __table_args__ = (
        CheckConstraint(
            "status_name IN ({})".format(
                ", ".join(f"'{status}'" for status in OrderStatuses)
            ),
            name="check_order_status",
        ),
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    logo_url: Mapped[str]
    is_folder: Mapped[bool]
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=True, index=True
    )
    filter_config: Mapped[list[dict]] = mapped_column(
        JSONB, nullable=True, default=list
    )

    parent: Mapped["Category | None"] = relationship(
        "Category", back_populates="children", remote_side=[id]
    )

    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="category"
    )
    __table_args__ = (UniqueConstraint("name", "parent_id", name="uix_name_parent_id"),)


class SuggestedCategory(Base):
    __tablename__ = "suggested_categories"

    name: Mapped[str] = mapped_column(primary_key=True)
    products_count: Mapped[int]
    status_name: Mapped[str]
    __table_args__ = (
        CheckConstraint(
            "status_name IN ({})".format(
                ", ".join(f"'{status}'" for status in SuggestionStatus)
            ),
            name="check_suggested_category_status",
        ),
    )


class OrderMessage(Base):
    __tablename__ = "order_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    sender_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
