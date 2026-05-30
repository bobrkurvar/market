import pytest

from domain import Product, ProductItem, ProductItemStatuses, ProductVariant, Seller


def test_product_item_reserve():
    item = ProductItem(content="content", product_variant_id=1)
    item.reserve(1)
    assert item.order_id == 1
    assert item.status == ProductItemStatuses.reserved


def test_product_item_release():
    item = ProductItem(content="content", product_variant_id=1)
    item.reserve(1)
    item.release()
    assert item.order_id is None
    assert item.status == ProductItemStatuses.available


def test_product_item_confirm_purchase_fail():
    item = ProductItem(content="content", product_variant_id=1)
    with pytest.raises(ValueError):
        item.confirm_purchase()


def test_product_item_confirm_purchase_success():
    item = ProductItem(content="content", product_variant_id=1)
    item.reserve(1)
    item.confirm_purchase()
    assert item.status == ProductItemStatuses.sold


def test_product_item_compromise_fail():
    item = ProductItem(content="content", product_variant_id=1)
    with pytest.raises(ValueError):
        item.compromise()


def test_product_item_compromise_success():
    item = ProductItem(content="content", product_variant_id=1)
    item.reserve(1)
    item.confirm_purchase()
    item.compromise()
    assert item.status == ProductItemStatuses.compromised


def test_create_product_variant_with_product_obj_without_id():
    product = Product(title="title", seller_id=1)
    product_variant = ProductVariant(price=1, product=product)
    assert product_variant


def test_create_product_variant_with_product_id_success():
    product_variant = ProductVariant(price=1, product_id=1)
    assert product_variant.product_id == 1


def test_create_product_variant_with_product_with_id_success():
    product = Product(title="title", product_id=1, seller_id=1)
    product_variant = ProductVariant(price=1, product=product)
    assert product_variant.product_id == product.id


def test_create_product_variant_with_product_with_id_and_with_product_id():
    product = Product(title="title", product_id=1, seller_id=1)
    product_variant = ProductVariant(price=1, product=product, product_id=2)
    assert product_variant.product_id == product.id

def test_create_product_variant_obj_with_wrong_price():
    with pytest.raises(ValueError, match="Цена не может быть отрицательной"):
        ProductVariant(price=-1, product_id=1)


def test_change_price_fail():
    product_variant = ProductVariant(price=11, product_id=1)
    with pytest.raises(ValueError, match="Новая цена не может быть отрицательной"):
        product_variant.change_price(-1)


def test_create_product_obj_without_seller():
    with pytest.raises(ValueError, match="Товар не может существовать без продавца"):
        Product(title="title")


def test_create_product_obj_with_seller_without_id():
    seller = Seller(username="username")
    with pytest.raises(ValueError, match="Товар не может существовать без продавца"):
        Product(title="title", seller=seller)


def test_create_product_obj_with_seller_with_id():
    seller = Seller(username="username", seller_id=1)
    product = Product(title="title", seller=seller)
    assert product