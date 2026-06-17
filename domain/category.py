from enum import StrEnum
from collections.abc import Collection

class CategoryAttr:
    def __init__(self, key: str, label: str, strict_options: bool = False, attr_type: str | None = None, options: Collection[str] | str | None = None):
        self.key = key
        self.label = label
        self.type = attr_type
        if not options:
            self.options = []
        elif isinstance(options, Collection):
            self.options = list(options)
        else:
            self.options = [options]
        self.strict_options = strict_options

class Category:
    def __init__(
        self,
        name: str,
        is_folder: bool,
        logo_url: str | None = None,
        category_id: int | None = None,
        parent_id: int | None = None,
        parent: "Category" = None,
        children: list["Category"] | None = None,
        filter_config: list[CategoryAttr] | None = None,
    ):
        self.name = name
        self.id = category_id
        self.parent = parent
        self.parent_id = parent.id if parent else parent_id
        self.logo_url = logo_url
        self.is_folder = is_folder
        self.children = children or []
        self.filter_config = filter_config or []

    def validate_parent(self, parent_category: "Category") -> None:
        """Проверяет, может ли переданная категория быть родителем для текущей."""
        if self.parent_id is None:
            return

        if parent_category.id != self.parent_id:
            raise ValueError(
                "ID переданного родителя не совпадает с parent_id текущей категории."
            )

        if not parent_category.is_folder:
            raise ValueError(
                "Нельзя создать вложенную категорию внутри товарного листа."
            )

    def add_default_child(self):
        if not self.is_folder:
            raise ValueError("Только папки могут иметь дочерние категории.")

        self.children.append(
            Category(
                name="Прочее",
                is_folder=False,
                logo_url=self.logo_url,
                filter_config=self.filter_config,
            )
        )

    @property
    def strict_filters_dict(self) -> dict:
        """
        Возвращает словарь обязательных фильтров для этой категории в формате:
        { "os": {"label": "Операционная система", "options": ["Windows", "macOS"]} }
        """
        req_filters = {}

        for attr in self.filter_config:
            if attr.strict_options and attr.options:
                req_filters[attr.key] = {
                    "label": attr.label,
                    "options": attr.options
                }

        return req_filters

    @property
    def parent_name(self) -> str | None:
        if self.parent:
            return self.parent.name
        return None

class SuggestionStatus(StrEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class SuggestedCategory:
    def __init__(
        self,
        name: str,
        products_count: int,
        status: SuggestionStatus = SuggestionStatus.pending,
    ):
        self.name = name
        self.status = status
        self.products_count = products_count
