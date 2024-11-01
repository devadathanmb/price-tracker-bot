"""Add last_checked_at column

Revision ID: 62443ee7d7f2
Revises: 1300aec45646
Create Date: 2024-10-31 21:06:14.434536

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62443ee7d7f2'
down_revision: Union[str, None] = '1300aec45646'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracked_items', sa.Column('last_checked_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tracked_items', 'last_checked_at')
    # ### end Alembic commands ###