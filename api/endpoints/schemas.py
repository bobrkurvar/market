from pydantic import BaseModel, Field, ConfigDict
from domain import UserRole, ProductVariant, ProductItem, Product, Seller

class BaseInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class UserLogin(BaseInput):
    username: str
    password: str

class UserRegister(BaseInput):
    username: str
    password: str
    role: UserRole



class ProductItemCreate(BaseInput):
    content: str

class ProductVariantCreate(BaseInput):
    price: float = Field(..., ge=0)
    attributes: dict = Field(default_factory=dict)
    items: list[ProductItemCreate] | None

    def to_domain(self) -> ProductVariant:
        domain_items = [
            ProductItem(content=item.content)
            for item in self.items
        ]
        return ProductVariant(
            price=self.price,
            attributes=self.attributes,
            items=domain_items
        )

class ProductCreate(BaseInput):
    title: str = Field(..., min_length=3, max_length=255)
    description: str
    variants: list[ProductVariantCreate] = Field(..., min_length=1)

    def to_domain(self, seller: Seller) -> Product:
        domain_variants = [variant.to_domain() for variant in self.variants]

        return Product(
            title=self.title,
            description=self.description,
            seller=seller,
            variants=domain_variants
        )

# class CartItemUpdate(BaseModel):
#     product_id: int
#     quantity: int
