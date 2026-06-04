from adapters.deps import UowDep
from api.schemas import CategoryOut
from fastapi import APIRouter
import logging
from domain import Category

log = logging.getLogger(__name__)

router = APIRouter(prefix="/categories")


@router.get("/{slug/{category_id}}", response_model=CategoryOut)
async def get_home_page(uow: UowDep, slug: str, category_id: int):
    async with uow:
        return uow.db.read_one(Category, category_id=category_id)