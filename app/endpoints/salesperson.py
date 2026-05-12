from fastapi import APIRouter, Depends, HTTPException
from .schemas import ProductResponse, ProductCreate
from adapters.deps import DbManagerDep
from domain import Salesperson, Product

router = APIRouter()


@router.post("/products", response_model=ProductResponse)
async def create_product(data: ProductCreate, db: DbManagerDep):
    """Создать описание товара (Витрину)"""
    new_product = Product(**data.model_dump())
    db.create(Product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


@router.post("/products/{product_id}/units")
async def add_product_units(
        product_id: int,
        units: list[ProductUnitCreate],
        db: DbManagerDep
):
    """Массовая загрузка ключей в товар"""
    new_units = [
        ProductUnit(product_id=product_id, content=u.content)
        for u in units
    ]
    db.add_all(new_units)
    # Здесь же можно обновить quantity в таблице Product
    await db.execute(
        update(Product)
        .where(Product.id == product_id)
        .values(quantity=Product.quantity + len(units))
    )
    await db.commit()
    return {"status": "added", "count": len(units)}



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