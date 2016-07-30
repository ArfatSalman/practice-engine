"""empty message

Revision ID: 4f733ced1ae1
Revises: 97ff50249734
Create Date: 2016-07-29 20:58:10.435000

"""

# revision identifiers, used by Alembic.
revision = '4f733ced1ae1'
down_revision = '97ff50249734'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('picture', sa.String(length=128), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'picture')

    ### end Alembic commands ###
