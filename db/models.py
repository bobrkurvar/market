
from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint, BigInteger, String, Text, DECIMAL
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from decimal import Decimal



class Base(AsyncAttrs, DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    salesperson_id: Mapped[int] = mapped_column(ForeignKey("salespersons.id"))

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float]

    stock: Mapped[list["ProductUnit"]] = relationship("ProductUnit", back_populates="product")
    salesperson: Mapped["Salesperson"] = relationship("Salesperson", back_populates="products")


class ProductUnit(Base):
    __tablename__ = "product_units"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    content: Mapped[str] = mapped_column(Text)
    is_sold: Mapped[bool] = mapped_column(default=False)

    product: Mapped["Product"] = relationship("Product", back_populates="stock")



class Salesperson(Base):
    __tablename__ = "salespersons"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    rating: Mapped[Decimal | None] = mapped_column(DECIMAL(2,1), server_default=None, default=None, nullable=True)
    products: Mapped[list["Product"]] = relationship("Product", back_populates="salesperson")


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    balance: Mapped[float]
    is_blocked: Mapped[bool] = mapped_column(default=False, server_default="false")
    cart: Mapped["Cart"] = relationship("Cart", back_populates="client")


class Cart(Base):
    __tablename__ = "cart"
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    quantity: Mapped[int]

    client: Mapped["Client"] = relationship("Client", back_populates="cart")
    product: Mapped["Product"] = relationship("Product")


class OrderStatus(Base):
    __tablename__ = "order_statuses"
    name: Mapped[str] = mapped_column(String(20), primary_key=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    status_name: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("order_statuses.name"),
        default="NEW",
        server_default="NEW"
    )

    status: Mapped["OrderStatus"] = relationship("OrderStatus")