"""empty message

Revision ID: 824b3cad7c83
Revises: a44954a3ed72
Create Date: 2020-06-21 09:52:28.145343

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '824b3cad7c83'
down_revision = 'a44954a3ed72'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cluster', sa.Column('cluster_type', sa.String(length=20), nullable=True, comment='集群类型,1、私有云 2、阿里云 3、AWS 4、Azure 5、青云 6、华为云 7、腾讯云'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cluster', 'cluster_type')
    # ### end Alembic commands ###
