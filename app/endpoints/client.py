from fastapi import APIRouter, Depends, HTTPException
from .schemas import ProductCreate
from adapters.deps import DbManagerDep

router = APIRouter()



# --- КОРЗИНА (Для покупателя) ---

@router.post("/cart/items")
async def add_to_cart(
        item: CartItemUpdate,
        client_id: int,
        db: DbManagerDep
):
    """Добавить в корзину с логикой ON CONFLICT (Upsert)"""
    stmt = pg_insert(Cart).values(
        client_id=client_id,
        product_id=item.product_id,
        quantity=item.quantity
    ).on_conflict_do_update(
        index_elements=['client_id', 'product_id'],
        set_={'quantity': Cart.quantity + item.quantity}
    )
    await db.execute(stmt)
    await db.commit()
    return {"message": "Cart updated"}


# --- ЗАКАЗ И ВЫДАЧА (Процесс покупки) ---

@router.post("/orders")
async def checkout(client_id: int, db: AsyncSession = Depends(get_db)):
    """Оформление заказа (Упрощенная транзакция)"""
    async with db.begin():  # Начинаем транзакцию
        # 1. Получаем айтемы из корзины
        # 2. Для каждого айтема ищем свободный ProductUnit
        # 3. Создаем Order
        # 4. Помечаем Unit как проданый и привязываем к Order
        # 5. Очищаем корзину

        # Это место для сложной логики выбора ключей
        pass
    return {"status": "success", "order_id": 123}


@router.get("/orders/{order_id}")
async def get_order_details(order_id: int, db: AsyncSession = Depends(get_db)):
    """Посмотреть детали заказа и получить ключ"""
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if order.status_name == "PAID":
        # Возвращаем информацию вместе с выданным контентом
        return {
            "id": order.id,
            "status": order.status_name,
            "content": order.delivered_content  # Тот самый ключ
        }
    return order