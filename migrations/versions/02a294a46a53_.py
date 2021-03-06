"""empty message

Revision ID: 02a294a46a53
Revises: 7e7bd8211da1
Create Date: 2020-07-15 22:52:13.564954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02a294a46a53'
down_revision = '7e7bd8211da1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cluster', sa.Column('status', sa.Integer(), nullable=True, comment='1:启用,0:禁用'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cluster', 'status')
    # ### end Alembic commands ###
