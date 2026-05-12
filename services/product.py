from domain import OrderStatuses, Product, Client, Order

async def make_order(
    manager,
    product: Product,
    client: Client
):
    order = Order(client=client, product=product)
    # до создания заказа должны запроситься способы оплаты и пройти все подготовительные этапы
    await manager.create(order)
    # должен запрашивать оплату и в случае чего отменять заказ
    # в случае подтверждения заказа в базе нужно и синхронизировать Product
