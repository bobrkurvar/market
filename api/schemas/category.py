from pydantic import BaseModel, computed_field
from domain import Category
from adapters.images import CategoryImagesManager
from .base import BaseInput
from slugify import slugify


class CategoryCreate(BaseInput):
    name: str
    parent_id: int | None = None

    def to_domain(self):
        return Category(name=self.name, parent_id=self.parent_id)


class CategoryImageOut(BaseModel):
    logo_url: str

    @computed_field
    @property
    def catalog_url(self) -> str | None:
        if not self.logo_url:
            return None
        return "/" + CategoryImagesManager().get_category_catalog_image_path(self.logo_url)

    @computed_field
    @property
    def search_url(self) -> str | None:
        if not self.logo_url:
            return None
        return "/" + CategoryImagesManager().get_category_search_image_path(self.logo_url)

    class Config:
        from_attributes = True


class CategoryAdminOut(CategoryImageOut):
    id: int
    name: str
    level: int
    has_children: bool


class CategoryOut(CategoryImageOut):
    id: int
    name: str
    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name)

    class Config:
        from_attributes = True


