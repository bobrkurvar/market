from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from adapters.deps import HttpClientDep, UowDep
from adapters.images import CategoryImagesManager, ImageGenerator
from api.schemas import CategoryAdminOut, CategoryCreate
from domain import Category, OrderMessage, Dispute, DisputeMessage
from infra.security import async_hash_calculate
from services.category import create_category
from adapters.deps import get_admin

router = APIRouter(prefix="/admin", dependencies=[Depends(get_admin)])


def get_category_form(data: Annotated[str, Form()]) -> CategoryCreate:
    return CategoryCreate.model_validate_json(data)


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
        img=await file.read(),
        hash_calculator=async_hash_calculate,
    )
    return {"category": category}


@router.get("/categories", response_model=list[CategoryAdminOut])
async def get_admin_categories(uow: UowDep):
    async with uow:
        return await uow.category.get_all_categories_tree_flat()


@router.delete("/categories/{category_id}")
async def admin_delete_category(category_id: int, uow: UowDep):
    async with uow:
        deleted_category = await uow.db.delete(
            Category, id=category_id, with_raise=True
        )
        return {"category": deleted_category}



@router.get("/orders/{order_id}/messages")
async def admin_get_chat_history(uow: UowDep, order_id: int):
    async with uow:
        return await uow.db.read(OrderMessage, order_id=order_id, order_by="created_at")


@router.get("/disputes")
async def admin_get_orders_disputes(uow: UowDep):
    async with uow:
        return await uow.db.read(Dispute)


@router.get("/disputes/{dispute_id}/messages")
async def admin_get_dispute_chat_history(uow: UowDep, dispute_id: int):
    async with uow:
        return await uow.db.read(DisputeMessage, dispute_id=dispute_id, order_by="created_at")

