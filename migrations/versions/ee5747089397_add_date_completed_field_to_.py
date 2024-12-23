"""Add date_completed field to ServiceRequest model.

Revision ID: ee5747089397
Revises: 2a56990769b1
Create Date: 2024-09-26 00:16:01.985254

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee5747089397'
down_revision = '2a56990769b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_completed', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('date_completed')

    # ### end Alembic commands ###
