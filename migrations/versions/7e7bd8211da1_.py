"""empty message

Revision ID: 7e7bd8211da1
Revises: d662e3eb08e7
Create Date: 2020-06-30 11:16:46.288787

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e7bd8211da1'
down_revision = 'd662e3eb08e7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('env', sa.Column('clusters', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('env', 'clusters')
    # ### end Alembic commands ###