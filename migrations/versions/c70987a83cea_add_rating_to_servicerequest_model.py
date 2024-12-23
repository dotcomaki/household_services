"""Add rating to ServiceRequest model

Revision ID: c70987a83cea
Revises: ec25cb651a9f
Create Date: 2024-11-09 15:19:05.412254

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c70987a83cea'
down_revision = 'ec25cb651a9f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_requests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rating', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_requests', schema=None) as batch_op:
        batch_op.drop_column('rating')

    # ### end Alembic commands ###
