"""init

Revision ID: a59be43ee34c
Revises: 
Create Date: 2026-06-23 19:14:35.185642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a59be43ee34c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('logo_url', sa.String(), nullable=False),
    sa.Column('is_folder', sa.Boolean(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('filter_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'parent_id', name='uix_name_parent_id')
    )
    op.create_index(op.f('ix_categories_parent_id'), 'categories', ['parent_id'], unique=False)
    op.create_table('suggested_categories',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('products_count', sa.Integer(), nullable=False),
    sa.Column('status_name', sa.String(), nullable=False),
    sa.CheckConstraint("status_name IN ('pending', 'approved', 'rejected')", name='check_suggested_category_status'),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('sellers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.DECIMAL(precision=2, scale=1), nullable=True),
    sa.Column('reviews_count', sa.Integer(), nullable=False),
    sa.Column('sales_count', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('suggested_category', sa.String(length=100), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('buyer_message', sa.Text(), nullable=True),
    sa.Column('is_archived', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_product_fts', 'products', [sa.literal_column("to_tsvector('russian', description)")], unique=False, postgresql_using='gin')
    op.create_index('idx_product_title_trgm', 'products', ['title'], unique=False, postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'})
    op.create_table('product_variants',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('product_id', sa.BigInteger(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('buyer_message', sa.Text(), nullable=True),
    sa.Column('stock', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('buyer_id', sa.Integer(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=True),
    sa.Column('product_variant_id', sa.BigInteger(), nullable=True),
    sa.Column('payment_link', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status_name', sa.String(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('product_snapshot', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.CheckConstraint("status_name IN ('pending_payments', 'paid', 'canceled', 'dispute')", name='check_order_status'),
    sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('disputes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.BigInteger(), nullable=False),
    sa.Column('opened_by_id', sa.Integer(), nullable=False),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('status_name', sa.String(), nullable=False),
    sa.Column('resolution', sa.Text(), nullable=True),
    sa.Column('resolved_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("status_name IN ('open', 'resolved')", name='check_dispute_status'),
    sa.ForeignKeyConstraint(['opened_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['resolved_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_id')
    )
    op.create_table('order_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.BigInteger(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_items',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('product_variant_id', sa.BigInteger(), nullable=False),
    sa.Column('order_id', sa.BigInteger(), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('status_name', sa.String(), nullable=False),
    sa.CheckConstraint("status_name IN ('available', 'reserved', 'sold', 'compromised')", name='check_product_item_status'),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reviews',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('order_id', sa.BigInteger(), nullable=False),
    sa.Column('product_id', sa.BigInteger(), nullable=False),
    sa.Column('product_variant_id', sa.BigInteger(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_id')
    )
    op.create_table('dispute_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dispute_id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['dispute_id'], ['disputes.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dispute_messages')
    op.drop_table('reviews')
    op.drop_table('product_items')
    op.drop_table('order_messages')
    op.drop_table('disputes')
    op.drop_table('orders')
    op.drop_table('product_variants')
    op.drop_index('idx_product_title_trgm', table_name='products', postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'})
    op.drop_index('idx_product_fts', table_name='products', postgresql_using='gin')
    op.drop_table('products')
    op.drop_table('sellers')
    op.drop_table('users')
    op.drop_table('suggested_categories')
    op.drop_index(op.f('ix_categories_parent_id'), table_name='categories')
    op.drop_table('categories')
    # ### end Alembic commands ###
