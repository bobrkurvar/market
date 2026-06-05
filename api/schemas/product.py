from pydantic import BaseModel, Field, computed_field
from domain import ProductVariant, ProductItem, Product, Seller
from adapters.images import ProductImagesManager
from slugify import slugify
from .base import BaseInput



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
            category_id=self.category_id,
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


class ProductImage(BaseModel):
    image_url: str

    @computed_field
    @property
    def catalog_url(self) -> str | None:
        if not self.image_url:
            return None
        return ProductImagesManager().get_product_catalog_image_path(self.image_url)

    @computed_field
    @property
    def detail_url(self) -> str | None:
        if not self.image_url:
            return None
        return ProductImagesManager().get_product_details_image_path(self.image_url)

    class Config:
        from_attributes = True


class ProductOut(ProductImage):
    id: int
    title: str
    description: str
    price: float

    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.title)


class ProductCatalogListOut(BaseModel):
    total: int | None = None
    items: list[ProductOut]


class ProductVariantDetailOut(BaseModel):
    id: int
    price: float
    attributes: dict | None

    class Config:
        from_attributes = True


class ProductDetailOut(ProductImage):
    id: int
    title: str
    description: str
    # Если ты хочешь вывести имя продавца:
    # seller_username: str | None = Field(default=None, alias="seller.username")
    variants: list[ProductVariantDetailOut]

    class Config:
        from_attributes = True
