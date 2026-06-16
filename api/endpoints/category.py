from adapters.deps import UowDep
from api.schemas import CategoryOut, FilterRule, FilterType
from fastapi import APIRouter
import logging
from domain import Category

log = logging.getLogger(__name__)

router = APIRouter(prefix="/categories")


@router.get("",  response_model=list[CategoryOut])
async def get_categories(uow: UowDep, limit: int = 8, offset: int = 0):
    async with uow:
        return await uow.db.read(Category, limit=limit, offset=offset)

# @router.get("/{slug}/{category_id}", response_model=CategoryOut)
# async def get_category(uow: UowDep, slug: str, category_id: int):
#     async with uow:
#         category = await uow.db.read_one(Category, id=category_id)
#         log.debug("Category: %s", category)
#         return category

@router.get("/{slug}/{category_id}", response_model=CategoryOut)
async def get_category(uow: UowDep, slug: str, category_id: int):
    async with uow:
        ancestors = await uow.category.get_category_branch(category_id)
        target_category = ancestors[-1]
        merged_filters: dict[str, FilterRule] = {
            "price": FilterRule(
                key="price",
                label="Цена",
                type=FilterType.RANGE
            )
        }
        for cat in ancestors:
            for f_rule in cat.filter_config:
                rule_obj = FilterRule(**f_rule)
                merged_filters[rule_obj.key] = rule_obj

        target_category.filter_config = list(merged_filters.values())

        return target_category