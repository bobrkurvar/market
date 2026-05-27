import pytest

from domain import Product, ProductItem, ProductItemStatuses


def test_product_item_reserve():
    item = ProductItem(content="content", product_id=1)
    item.reserve(1)
    assert item.order_id == 1
    assert item.status == ProductItemStatuses.reserved


def test_product_item_release():
    item = ProductItem(content="content", product_id=1)
    item.reserve(1)
    item.release()
    assert item.order_id is None
    assert item.status == ProductItemStatuses.available


def test_product_item_confirm_purchase_fail():
    item = ProductItem(content="content", product_id=1)
    with pytest.raises(ValueError):
        item.confirm_purchase()


def test_product_item_confirm_purchase_success():
    item = ProductItem(content="content", product_id=1)
    item.reserve(1)
    item.confirm_purchase()
    assert item.status == ProductItemStatuses.sold


def test_product_item_compromise_fail():
    item = ProductItem(content="content", product_id=1)
    with pytest.raises(ValueError):
        item.compromise()


def test_product_item_compromise_success():
    item = ProductItem(content="content", product_id=1)
    item.reserve(1)
    item.confirm_purchase()
    item.compromise()
    assert item.status == ProductItemStatuses.compromised


def test_create_product_obj_with_wrong_price():
    with pytest.raises(ValueError, match="Цена не может быть отрицательной"):
        Product(title="title", seller_id=1, price=-1)


def test_create_product_obj_without_seller():
    with pytest.raises(ValueError, match="Товар не может существовать без продавца"):
        Product(title="title", price=7)


def test_change_price_fail():
    product = Product(title="title", seller_id=1, price=11)
    with pytest.raises(ValueError, match="Новая цена не может быть отрицательной"):
        product.change_price(-1)
