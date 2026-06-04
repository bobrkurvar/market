"""init

Revision ID: 1796b5d7573e
Revises: 
Create Date: 2026-06-04 09:59:23.497736

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1796b5d7573e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('logo_url', sa.String(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_categories_parent_id'), 'categories', ['parent_id'], unique=False)
    op.create_table('order_statuses',
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('product_item_statuses',
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('routes',
    sa.Column('value', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('value', 'slug')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('is_blocked', sa.Boolean(), server_default='false', nullable=False),
    sa.ForeignKeyConstraint(['id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sellers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.DECIMAL(precision=2, scale=1), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_product_fts', 'products', [sa.literal_column("to_tsvector('russian', title)")], unique=False, postgresql_using='gin')
    op.create_index('idx_product_title_trgm', 'products', ['title'], unique=False, postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'})
    op.create_table('product_variants',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('product_id', sa.BigInteger(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('product_variant_id', sa.BigInteger(), nullable=True),
    sa.Column('payment_link', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('status_name', sa.String(length=20), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('product_snapshot', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['status_name'], ['order_statuses.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_items',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('product_variant_id', sa.BigInteger(), nullable=False),
    sa.Column('order_id', sa.BigInteger(), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('status_name', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['status_name'], ['product_item_statuses.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product_items')
    op.drop_table('orders')
    op.drop_table('product_variants')
    op.drop_index('idx_product_title_trgm', table_name='products', postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'})
    op.drop_index('idx_product_fts', table_name='products', postgresql_using='gin')
    op.drop_table('products')
    op.drop_table('sellers')
    op.drop_table('clients')
    op.drop_table('users')
    op.drop_table('routes')
    op.drop_table('product_item_statuses')
    op.drop_table('order_statuses')
    op.drop_index(op.f('ix_categories_parent_id'), table_name='categories')
    op.drop_table('categories')
    # ### end Alembic commands ###
