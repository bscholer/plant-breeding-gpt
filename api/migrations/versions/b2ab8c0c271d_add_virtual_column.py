"""Add virtual column

Revision ID: b2ab8c0c271d
Revises: bdb4c73c7e31
Create Date: 2023-11-17 22:43:00.444173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b2ab8c0c271d'
down_revision: Union[str, None] = 'bdb4c73c7e31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    pass
# def upgrade():
#     op.execute("""
#         ALTER TABLE plants
#         ADD COLUMN plant_type VARCHAR(255) AS (
#             SELECT variety
#             FROM seeds
#             WHERE seeds.seed_id = plants.seed_id
#         ) VIRTUAL
#     """)


def downgrade() -> None:
    # op.execute("ALTER TABLE plants DROP COLUMN plant_type")
    pass
