"""empty message

Revision ID: dd08ad1d1c69
Revises: 7e04b251b97d
Create Date: 2016-07-08 20:01:08.394000

"""

# revision identifiers, used by Alembic.
revision = 'dd08ad1d1c69'
down_revision = '7e04b251b97d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('solutions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column(u'questions', 'author_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.drop_column(u'questions', 'difficulty_index')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(u'questions', sa.Column('difficulty_index', mysql.FLOAT(), nullable=True))
    op.alter_column(u'questions', 'author_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.drop_table('solutions')
    ### end Alembic commands ###