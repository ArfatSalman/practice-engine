"""empty message

Revision ID: f3fcad830786
Revises: 5abc219f7fe4
Create Date: 2016-06-29 10:14:26.947000

"""

# revision identifiers, used by Alembic.
revision = 'f3fcad830786'
down_revision = '5abc219f7fe4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('downvote_question_assoc',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'question_id')
    )
    op.create_table('favourite_question_assoc',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'question_id')
    )
    op.create_table('upvote_question_assoc',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'question_id')
    )
    op.add_column(u'questions', sa.Column('disabled', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'questions', 'disabled')
    op.drop_table('upvote_question_assoc')
    op.drop_table('favourite_question_assoc')
    op.drop_table('downvote_question_assoc')
    ### end Alembic commands ###
