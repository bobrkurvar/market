from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, BigInteger, ForeignKey, String, Text, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"))

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float]

    items: Mapped[list["ProductItem"]] = relationship(
        "ProductItem",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    seller: Mapped["Seller"] = relationship("Seller", back_populates="products")


class ProductItemStatuses(Base):
    __tablename__ = "product_item_statuses"
    name: Mapped[str] = mapped_column(primary_key=True)


class ProductItem(Base):
    __tablename__ = "product_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    status_name: Mapped[str] = mapped_column(ForeignKey("product_item_statuses.name"))

    # product: Mapped["Product"] = relationship("Product", back_populates="stock")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_on": "type",  # Указываем, что наследование полиморфно по этому полю
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


class Client(User):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    is_blocked: Mapped[bool] = mapped_column(default=False, server_default="false")
    # cart: Mapped["Cart"] = relationship("Cart", back_populates="client")
    __mapper_args__ = {
        "polymorphic_identity": "client",  # Значение для колонки users.type
    }


# class Cart(Base):
#     __tablename__ = "cart"
#     client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), primary_key=True)
#     product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
#     quantity: Mapped[int]
#
#     client: Mapped["Client"] = relationship("Client", back_populates="cart")
#     product: Mapped["Product"] = relationship("Product")


class OrderStatuses(Base):
    __tablename__ = "order_statuses"
    name: Mapped[str] = mapped_column(String(20), primary_key=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL")
    )
    payment_link: Mapped[str | None] = mapped_column(default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    status_name: Mapped[str] = mapped_column(
        ForeignKey("order_statuses.name"),
    )
    items: Mapped[list["ProductItem"]] = relationship("ProductItem")
    client: Mapped["Client"] = relationship("Client")
    price: Mapped[float]
    amount: Mapped[int]
    product_snapshot: Mapped[dict] = mapped_column(JSONB, default={}, server_default='{}')
    #seller: Mapped["Seller"] = relationship("Seller")
