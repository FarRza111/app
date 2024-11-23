"""empty message

Revision ID: ff9bd84cfba2
Revises: 9cd47a7d63fb, create_blog_posts_table
Create Date: 2024-11-23 20:26:25.049933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff9bd84cfba2'
down_revision: Union[str, None] = ('9cd47a7d63fb', 'create_blog_posts_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
