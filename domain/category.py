from enum import StrEnum


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
        filter_config: list[dict] | None = None
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
            raise ValueError("ID переданного родителя не совпадает с parent_id текущей категории.")

        if not parent_category.is_folder:
            raise ValueError("Нельзя создать вложенную категорию внутри товарного листа.")

    def add_default_child(self):
        if not self.is_folder:
            raise ValueError("Только папки могут иметь дочерние категории.")

        self.children.append(
            Category(
                name="Прочее",
                is_folder=False,
                logo_url=self.logo_url,
                filter_config=self.filter_config
            )
        )


class SuggestionStatus(StrEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class SuggestedCategory:
    def __init__(
        self,
        name: str,
        products_count: int,
        status: SuggestionStatus = SuggestionStatus.pending
    ):
        self.name = name
        self.status = status
        self.products_count = products_count