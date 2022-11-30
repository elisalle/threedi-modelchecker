"""breach and exchange

Revision ID: 0211
Revises: 0210
Create Date: 2022-11-23 11:21:10.967235

"""
from alembic import op

import geoalchemy2
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0211"
down_revision = "0210"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "v2_exchange_line",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.Column(
            "the_geom",
            geoalchemy2.types.Geometry(
                geometry_type="LINESTRING",
                srid=4326,
                management=True,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "v2_potential_breach",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.Column(
            "the_geom",
            geoalchemy2.types.Geometry(
                geometry_type="LINESTRING",
                srid=4326,
                management=True,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("v2_potential_breach")
    op.drop_table("v2_exchange_line")
