"""add super user

Revision ID: 9d6648e02bfb
Revises: 03838d5ae179
Create Date: 2017-06-09 14:40:56.125696

"""
from alembic import op
import sqlalchemy as sa
from config.database_config import SUPER_USER_FIRST_NAME, SUPER_USER_LAST_NAME, SUPER_USER_EMAIL


# revision identifiers, used by Alembic.
revision = '9d6648e02bfb'
down_revision = '03838d5ae179'
branch_labels = None
depends_on = None

# Create an ad-hoc tables to use for the insert and delete statements.
member_table = sa.table('members',
                        sa.Column('id', sa.Integer),
                        sa.Column('first_name', sa.String),
                        sa.Column('last_name', sa.String),
                        sa.Column('email_address', sa.String)
                        )

role_table = sa.table('roles',
                      sa.Column('member_id', sa.Integer),
                      sa.Column('role', sa.String))


def upgrade():

    op.bulk_insert(member_table, [{'id': 1, 'first_name': SUPER_USER_FIRST_NAME,
                    'last_name': SUPER_USER_LAST_NAME, 'email_address': SUPER_USER_EMAIL}])


    op.bulk_insert(role_table, [{'member_id': 1, 'role': 'admin'}])


def downgrade():
    op.execute(
        role_table.delete().where(role_table.c.member_id == 1)
    )
    op.execute(
        member_table.delete().where(member_table.c.id == 1)
    )
    pass
