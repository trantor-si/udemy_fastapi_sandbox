"""create apt_num for address col

Revision ID: bce26d4e1af0
Revises: 6f5e34c4d2cb
Create Date: 2022-11-07 20:50:02.605134

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'bce26d4e1af0'
down_revision = '6f5e34c4d2cb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('address', sa.Column('apt_num', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('address', 'apt_num')
