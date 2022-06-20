"""partner_user and partner_subscription

Revision ID: 82d3c7109ffb
Revises: 2b1d3cd93e4b
Create Date: 2022-06-09 08:25:09.078840

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82d3c7109ffb'
down_revision = '2b1d3cd93e4b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('partner_subscription',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sqlalchemy_utils.types.arrow.ArrowType(), nullable=False),
    sa.Column('updated_at', sqlalchemy_utils.types.arrow.ArrowType(), nullable=True),
    sa.Column('partner_user_id', sa.Integer(), nullable=False),
    sa.Column('end_at', sqlalchemy_utils.types.arrow.ArrowType(), nullable=False),
    sa.ForeignKeyConstraint(['partner_user_id'], ['partner_user.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('partner_user_id')
    )
    op.add_column('partner_user', sa.Column('external_user_id', sa.String(length=128), nullable=True))
    op.create_unique_constraint('uq_partner_id_external_user_id', 'partner_user', ['partner_id', 'external_user_id'])
    op.drop_index('ix_partner_user_user_id', table_name='partner_user')
    op.create_index(op.f('ix_partner_user_user_id'), 'partner_user', ['user_id'], unique=True)
    op.drop_constraint('uq_user_id_partner_id', 'partner_user', type_='unique')
    op.drop_constraint('uq_partner_id_partner_user_id', 'users', type_='unique')
    op.drop_column('users', 'partner_id')
    op.drop_column('users', 'partner_user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('partner_user_id', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('partner_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_unique_constraint('uq_partner_id_partner_user_id', 'users', ['partner_id', 'partner_user_id'])
    op.create_unique_constraint('uq_user_id_partner_id', 'partner_user', ['user_id', 'partner_id'])
    op.drop_index(op.f('ix_partner_user_user_id'), table_name='partner_user')
    op.create_index('ix_partner_user_user_id', 'partner_user', ['user_id'], unique=False)
    op.drop_constraint('uq_partner_id_external_user_id', 'partner_user', type_='unique')
    op.drop_column('partner_user', 'external_user_id')
    op.drop_table('partner_subscription')
    # ### end Alembic commands ###