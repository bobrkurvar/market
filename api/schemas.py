from pydantic import BaseModel, Field, ConfigDict, computed_field
from domain import UserRole, ProductVariant, ProductItem, Product, Seller, Category
from pathlib import Path
from adapters.images import ProductImagesManager

class BaseInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

class CategoryCreate(BaseInput):
    name: str
    parent_id: int | None = None

    def to_domain(self):
        return Category(name=self.name, parent_id=self.parent_id)


class CategoryAdminResponseSchema(BaseInput):
    id: int
    name: str
    level: int
    has_children: bool


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
    category_id: int

    def to_domain(self, seller: Seller) -> Product:
        domain_variants = [variant.to_domain() for variant in self.variants]

        return Product(
            title=self.title,
            description=self.description,
            seller=seller,
            variants=domain_variants,
            category_id=self.category_id
        )

class ProductVariantOut(BaseModel):
    id: int | None
    price: float
    attributes: dict | None

    class Config:
        from_attributes = True

class ProductSellerListOut(BaseModel):
    id: int | None
    title: str
    description: str
    items_count: int
    variants_count: int
    variants: list[ProductVariantOut]

    class Config:
        from_attributes = True

class ProductCatalogOut(BaseModel):
    id: int
    title: str
    description: str
    price: float
    image_url: str

    @computed_field
    @property
    def thumbnail_url(self) -> str | None:
        if not self.image_url:
            return None
        return ProductImagesManager().get_product_catalog_image_path(self.image_url)

    class Config:
        from_attributes = True


class ProductCatalogListOut(BaseModel):
    total: int
    items: list[ProductCatalogOut]


class ProductVariantDetailOut(BaseModel):
    id: int
    price: float
    attributes: dict | None

    class Config:
        from_attributes = True


class ProductDetailOut(BaseModel):
    id: int
    title: str
    description: str
    # Если ты хочешь вывести имя продавца:
    # seller_username: str | None = Field(default=None, alias="seller.username")
    variants: list[ProductVariantDetailOut]

    class Config:
        from_attributes = True
