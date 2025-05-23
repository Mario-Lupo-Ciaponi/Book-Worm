"""Added constraints.

Revision ID: 0ad155cffa1d
Revises: d32550a68b62
Create Date: 2025-04-23 15:04:56.884870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ad155cffa1d'
down_revision: Union[str, None] = 'd32550a68b62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('books', 'genre',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.alter_column('books', 'year',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('books', 'isbn',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
    op.alter_column('books', 'description',
               existing_type=sa.TEXT(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('books', 'description',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('books', 'isbn',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
    op.alter_column('books', 'year',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('books', 'genre',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    # ### end Alembic commands ###
