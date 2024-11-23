"""add author to blog posts

Revision ID: add_author_to_blog_posts
Revises: fix_courses_author
Create Date: 2024-01-23 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_author_to_blog_posts'
down_revision = 'fix_courses_author'
branch_labels = None
depends_on = None

def upgrade():
    # Add author_id column to blog_posts table
    op.add_column('blog_posts', sa.Column('author_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_blog_posts_author_id_users',
        'blog_posts', 'users',
        ['author_id'], ['id']
    )

def downgrade():
    # Drop foreign key constraint first
    op.drop_constraint('fk_blog_posts_author_id_users', 'blog_posts', type_='foreignkey')
    
    # Drop the author_id column
    op.drop_column('blog_posts', 'author_id')
