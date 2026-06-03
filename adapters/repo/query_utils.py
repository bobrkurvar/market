from sqlalchemy import Select, and_
from db.models import Product, ProductVariant, ProductItem
from domain import ProductItemStatuses

def apply_sold_items_filter(stmt: Select, is_outer=False) -> Select:
    """
    Добавляет к запросу JOIN'ы для вариантов и проданных ключей (айтемов).
    Ожидается, что модель Product уже участвует в запросе (либо как FROM, либо через JOIN).
    """
    if is_outer:
        return (
            stmt
            .outerjoin(ProductVariant, ProductVariant.product_id == Product.id)
            .outerjoin(
                ProductItem,
                and_(
                    ProductItem.product_variant_id == ProductVariant.id,
                    ProductItem.status_name == ProductItemStatuses.sold
                )
            )
        )
    else:
        return (
            stmt
            .join(ProductVariant, ProductVariant.product_id == Product.id)
            .join(ProductItem, ProductItem.product_variant_id == ProductVariant.id)
            .where(ProductItem.status_name == ProductItemStatuses.sold)
        )