import pytest

from domain import Client, Order, OrderStatuses, ProductVariant, ProductItem


def test_create_order_obj_without_client_and_client_id():
    with pytest.raises(ValueError, match="Заказ не может существовать без клиента"):
        Order(price=1)


def test_create_order_obj_without_product_and_product_id():
    with pytest.raises(ValueError, match="Заказ не может существовать без товара"):
        Order(client_id=1, price=1)


def test_create_order_obj_with_client_id_and_product_id():
    order = Order(client_id=1, product_variant_id=1, price=1)
    assert order.status == OrderStatuses.pending_payments and order.is_pending()


def test_create_order_obj_with_client_and_product():
    order = Order(
        client_id=1,
        price=1,
        product_variant_id=1,
        product_variant=ProductVariant(product_variant_id=2, price=7, product_id=5),
        client=Client(username="username", client_id=2, password="password"),
    )
    assert order.client_id == 2 and order.product_variant_id == 2


def test_create_order_obj_with_new_client():
    product_variant = ProductVariant(product_id=1, price=7, product_variant_id=2)
    client = Client(username="username", password="password")
    order = Order(client_id=1, product_variant=product_variant, client=client, price=1)
    assert order.client_id is None


def test_create_order_obj_with_items():
    with pytest.raises(
        ValueError,
        match="Нельзя передавать товарные позиции при инициализации нового заказа",
    ):
        Order(
            client_id=1,
            product_variant_id=1,
            price=1,
            items=ProductItem(content="content", product_variant_id=1),
        )


def test_cancel_order_fail_with_none_items():
    order = Order(client_id=1, product_variant_id=1, price=1)
    with pytest.raises(ValueError, match="Заказ не может быть без товарных позиций"):
        order.cancel()


def test_cancel_order_fail_with_empty_list_items():
    order = Order(client_id=1, product_variant_id=1, items=[], price=1)
    with pytest.raises(ValueError, match="Заказ без товаров"):
        order.cancel()


def test_pay_order_without_reserve_item():
    order = Order(
        order_id=1,
        client_id=1,
        price=1,
        product_variant_id=1,
        items=ProductItem(content="content", product_variant_id=1),
    )
    with pytest.raises(ValueError, match="Нельзя продать не зарезервированный ключ"):
        order.pay()


def test_cancel_paid_order():
    item = ProductItem(content="content", product_variant_id=1)
    order = Order(order_id=1, client_id=1, product_variant_id=1, items=[], price=1)
    order.reserve_items(item)
    order.pay()
    with pytest.raises(ValueError, match="Заказ уже оплачен"):
        order.cancel()


def test_cancel_order_success():
    item = ProductItem(content="content", product_variant_id=1)
    order = Order(order_id=1, client_id=1, product_variant_id=1, items=item, price=1)
    order.cancel()
    assert order.status == OrderStatuses.cancelled and order.is_cancelled()


def test_pay_order_without_items_fail():
    order = Order(client_id=1, product_variant_id=1, price=1)
    with pytest.raises(ValueError, match="Заказ не может быть без товарных позиций"):
        order.pay()


def test_pay_order_success():
    item = ProductItem(content="content", product_variant_id=1)
    order = Order(order_id=1, client_id=1, product_variant_id=1, items=[], price=1)
    order.reserve_items(item)
    order.pay()
    assert order.status == OrderStatuses.paid and order.is_paid()
