from pydantic import BaseModel, computed_field, Field
from domain import Category
from adapters.images import CategoryImagesManager
from .base import BaseInput
from slugify import slugify
from enum import StrEnum

class FilterType(StrEnum):
    CHECKBOX = "checkbox"
    SELECT = "select"
    RADIO = "radio"
    RANGE = "range"

class FilterRule(BaseModel):
    key: str
    label: str
    type: FilterType
    options: list[str] | None = None


class CategoryCreate(BaseInput):
    name: str
    parent_id: int | None = None
    filter_config: list[FilterRule] = Field(default_factory=list)

    def to_domain(self):
        return Category(
            name=self.name,
            parent_id=self.parent_id,
            is_folder=True,
            filter_config=[fil.model_dump() for fil in  self.filter_config]
        )


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
    parent: "CategoryOut | None" = None
    filter_config: list[FilterRule] | None = None
    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name)

    class Config:
        from_attributes = True


