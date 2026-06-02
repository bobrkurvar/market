from fastapi import APIRouter, Depends, status
from adapters.deps import UowDep
from domain import Category
from api.schemas import CategoryCreate, CategoryAdminResponseSchema

router = APIRouter(prefix="/admin")


@router.get("/categories", response_model=list[CategoryAdminResponseSchema])
async def get_admin_categories(uow: UowDep):
    async with uow:
        return await uow.category.get_all_categories_tree_flat()


@router.post("/category")
async def create_category(category: CategoryCreate, uow: UowDep):
    async with uow:
        new_category = category.to_domain()
        created_category = await uow.db.create(new_category)
    return {"category": created_category}


@router.delete("/categories/{category_id}")
async def delete_category(category_id: int, uow: UowDep):
    async with uow:
        deleted_category = await uow.db.delete(Category, id=category_id, with_raise=True)
        return {"category": deleted_category}