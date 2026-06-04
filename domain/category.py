class Category:
    def __init__(
        self,
        name: str,
        logo_url: str | None = None,
        category_id: int | None = None,
        parent_id: int | None = None
    ):
        self.name = name
        self.id = category_id
        self.parent_id = parent_id
        self.logo_url = logo_url