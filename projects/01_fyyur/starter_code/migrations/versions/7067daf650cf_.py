"""empty message

Revision ID: 7067daf650cf
Revises: 323a3a749c74
Create Date: 2022-06-04 20:17:08.512460

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7067daf650cf'
down_revision = '323a3a749c74'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artists', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('venues', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('venues', 'genres',
               existing_type=sa.VARCHAR())
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venues', 'genres',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('venues', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artists', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###