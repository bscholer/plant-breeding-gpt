"""move species and variety to seed

Revision ID: c2cf0b6ddbd7
Revises: 4c1c608620b0
Create Date: 2023-11-17 01:51:17.827064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c2cf0b6ddbd7'
down_revision: Union[str, None] = '4c1c608620b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('plants', 'species')
    op.drop_column('plants', 'variety')
    op.add_column('seeds', sa.Column('species', sa.String(length=255), nullable=True))
    op.add_column('seeds', sa.Column('variety', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('seeds', 'variety')
    op.drop_column('seeds', 'species')
    op.add_column('plants', sa.Column('variety', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('plants', sa.Column('species', mysql.VARCHAR(length=255), nullable=True))
    # ### end Alembic commands ###
