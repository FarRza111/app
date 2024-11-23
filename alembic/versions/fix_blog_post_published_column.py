"""fix blog post published column

Revision ID: fix_blog_post_published_column
Revises: add_author_to_blog_posts
Create Date: 2024-01-23 12:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_blog_post_published_column'
down_revision = 'add_author_to_blog_posts'
branch_labels = None
depends_on = None

def upgrade():
    # Rename is_published to published
    op.alter_column('blog_posts', 'is_published',
                    new_column_name='published',
                    existing_type=sa.Boolean(),
                    existing_nullable=True,
                    existing_server_default=sa.text('false'))

def downgrade():
    # Rename published back to is_published
    op.alter_column('blog_posts', 'published',
                    new_column_name='is_published',
                    existing_type=sa.Boolean(),
                    existing_nullable=True,
                    existing_server_default=sa.text('false'))
