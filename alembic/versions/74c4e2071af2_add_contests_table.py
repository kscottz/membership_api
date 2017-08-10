"""add contests table

Revision ID: 74c4e2071af2
Revises: 0d0f30daff78
Create Date: 2017-08-10 15:41:50.216572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74c4e2071af2'
down_revision = '0d0f30daff78'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'contests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('election_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=45), nullable=False),
        sa.Column('number_winners', sa.Integer(), nullable=True),
        sa.Column('count_rules', sa.String(length=254), nullable=False),
        sa.Column('count_for', sa.Integer(), nullable=False),
        sa.Column('count_against', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['election_id'], ['elections.id']),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('election_id')
    )


def downgrade():
    op.drop_table('contests')
