"""Initial migration

Revision ID: 4c1c608620b0
Revises: 4c984c0aae01
Create Date: 2023-11-16 23:30:04.620994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c1c608620b0'
down_revision: Union[str, None] = '4c984c0aae01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plants', sa.Column('seed_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'plants', 'seeds', ['seed_id'], ['seed_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'plants', type_='foreignkey')
    op.drop_column('plants', 'seed_id')
    # ### end Alembic commands ###