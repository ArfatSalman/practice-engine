"""empty message

Revision ID: 97ff50249734
Revises: 69a30bd6b410
Create Date: 2016-07-18 14:49:06.966000

"""

# revision identifiers, used by Alembic.
revision = '97ff50249734'
down_revision = '69a30bd6b410'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('questions', sa.Column('views', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('last_seen', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_seen')
    op.alter_column('user_settings', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.drop_column('questions', 'views')
    ### end Alembic commands ###