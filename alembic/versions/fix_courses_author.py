"""fix courses author

Revision ID: fix_courses_author
Revises: baa036ff4db3
Create Date: 2024-01-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fix_courses_author'
down_revision = 'baa036ff4db3'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Add author_id column
    op.add_column('courses', sa.Column('author_id', sa.Integer(), nullable=True))
    
    # 2. Create foreign key to users table
    op.create_foreign_key(
        'fk_courses_author_id_users',
        'courses', 'users',
        ['author_id'], ['id']
    )
    
    # 3. Drop the old foreign key to teachers
    op.drop_constraint('courses_teacher_id_fkey', 'courses', type_='foreignkey')
    
    # 4. Drop the old teacher_id column
    op.drop_column('courses', 'teacher_id')

def downgrade():
    # 1. Add back teacher_id column
    op.add_column('courses', sa.Column('teacher_id', sa.Integer(), nullable=True))
    
    # 2. Create foreign key to teachers table
    op.create_foreign_key(
        'courses_teacher_id_fkey',
        'courses', 'teachers',
        ['teacher_id'], ['id']
    )
    
    # 3. Drop the new foreign key to users
    op.drop_constraint('fk_courses_author_id_users', 'courses', type_='foreignkey')
    
    # 4. Drop the new author_id column
    op.drop_column('courses', 'author_id')
