"""Default value for cool_norm

Revision ID: b923bf100b1b
Revises: af764874ed27
Create Date: 2024-07-23 15:31:01.624043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b923bf100b1b'
down_revision = 'af764874ed27'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('cool_norm',
               existing_type=sa.FLOAT(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('cool_norm',
               existing_type=sa.FLOAT(),
               nullable=True)

    # ### end Alembic commands ###
