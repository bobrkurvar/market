from enum import StrEnum

from pydantic import BaseModel, Field, computed_field
from slugify import slugify

from adapters.images import CategoryImagesManager
from domain import Category, CategoryAttr

from .base import BaseInput


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
    strict_options: bool = False


class CategoryCreate(BaseInput):
    name: str
    parent_id: int | None = None
    filter_config: list[FilterRule] = Field(default_factory=list)

    def to_domain(self) -> Category:
        domain_filters = [
            CategoryAttr(
                key=rule.key,
                label=rule.label,
                strict_options=rule.strict_options,
                options=rule.options,
                attr_type=rule.type
            )
            for rule in self.filter_config
        ]

        return Category(
            name=self.name,
            parent_id=self.parent_id,
            is_folder=True,
            filter_config=domain_filters
        )


class CategoryImageOut(BaseModel):
    logo_url: str = Field(exclude=True)

    @computed_field
    @property
    def catalog_url(self) -> str | None:
        if not self.logo_url:
            return None
        return "/" + CategoryImagesManager().get_category_catalog_image_path(
            self.logo_url
        )

    @computed_field
    @property
    def search_url(self) -> str | None:
        if not self.logo_url:
            return None
        return "/" + CategoryImagesManager().get_category_search_image_path(
            self.logo_url
        )

    class Config:
        from_attributes = True


class CategoryAdminOut(CategoryImageOut):
    id: int
    name: str
    level: int
    has_children: bool


class CategoryShortOut(CategoryImageOut):
    id: int
    name: str

    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name)

    class Config:
        from_attributes = True


class CategoryOut(CategoryShortOut):
    parent_name: str | None = None
    children: list[CategoryShortOut] | None = None
    filter_config: list[FilterRule] | None = None
    is_folder: bool

    @computed_field
    @property
    def slug(self) -> str:
        return slugify(self.name)

    class Config:
        from_attributes = True


# class CategoryOut(CategoryImageOut):
#     id: int
#     name: str
#     parent: "CategoryOut | None" = None
#     filter_config: list[FilterRule] | None = None
#
#     @computed_field
#     @property
#     def slug(self) -> str:
#         return slugify(self.name)
#
#     class Config:
#         from_attributes = True
