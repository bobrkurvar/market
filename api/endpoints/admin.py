from fastapi import APIRouter, Depends, Form, UploadFile, File
from adapters.deps import UowDep, HttpClientDep
from domain import Category
from api.schemas import CategoryCreate, CategoryAdminOut
from services.category import create_category
from adapters.images import CategoryImagesManager, ImageGenerator
from typing import Annotated

router = APIRouter(prefix="/admin")

def get_category_form(
    name: Annotated[str, Form()],
    parent_id: Annotated[int | None, Form()] = None
) -> CategoryCreate:
    return CategoryCreate(
        name=name,
        parent_id=parent_id,
    )

@router.post("/categories")
async def admin_create_category(
    category_dto: Annotated[CategoryCreate, Depends(get_category_form)],
    uow: UowDep,
    http_client: HttpClientDep,
    file: Annotated[UploadFile, File()],
):
    category = await create_category(
        uow=uow,
        category=category_dto.to_domain(),
        file_manager=CategoryImagesManager(),
        img_generator=ImageGenerator(http_client),
        img=await file.read()
    )
    return {"category": category}


@router.get("/categories", response_model=list[CategoryAdminOut])
async def get_admin_categories(uow: UowDep):
    async with uow:
        return await uow.category.get_all_categories_tree_flat()



@router.delete("/categories/{category_id}")
async def admin_delete_category(category_id: int, uow: UowDep):
    async with uow:
        deleted_category = await uow.db.delete(Category, id=category_id, with_raise=True)
        return {"category": deleted_category}