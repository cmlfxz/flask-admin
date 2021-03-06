"""empty message

Revision ID: c118d38df6c0
Revises: a8d1c49d8194
Create Date: 2020-06-04 10:11:17.161782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c118d38df6c0'
down_revision = 'a8d1c49d8194'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('server_info', sa.Column('server_region', sa.String(length=30), nullable=True, comment='地区'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('server_info', 'server_region')
    # ### end Alembic commands ###
