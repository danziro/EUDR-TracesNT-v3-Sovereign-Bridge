import geoalchemy2

"""baseline_master_v1

Revision ID: c209c1826454
Revises: 
Create Date: 2026-06-08 14:40:50.987266

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c209c1826454'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Aktifkan PostGIS dan UUID Generator
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # 2. Tabel HGU Prioritas 1
    op.execute("""
        CREATE TABLE hgu_prioritas_1 (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            nomor_sertifikat VARCHAR UNIQUE NOT NULL,
            pemegang_hak VARCHAR NOT NULL,
            luas_sertifikat_ha DOUBLE PRECISION NOT NULL,
            geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)
    op.execute("CREATE INDEX idx_hgu_geom ON hgu_prioritas_1 USING GIST (geom);")

    # 3. Tabel Kawasan Hutan Prioritas 3
    op.execute("""
        CREATE TABLE kawasan_hutan_prioritas_3 (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            nama_kawasan VARCHAR NOT NULL,
            fungsi_hutan VARCHAR NOT NULL,
            sk_menhut VARCHAR,
            geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)
    op.execute("CREATE INDEX idx_hutan_geom ON kawasan_hutan_prioritas_3 USING GIST (geom);")

    # 4. Tabel Lahan (Plots) dengan Kolom H3 Indices
    op.execute("""
        CREATE TABLE plots (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            plot_id VARCHAR UNIQUE NOT NULL,
            farmer_name VARCHAR NOT NULL,
            nib VARCHAR NOT NULL,
            commodity VARCHAR DEFAULT 'Oil Palm' NOT NULL,
            area_ha DOUBLE PRECISION NOT NULL,
            annual_quantity_estimate_mt DOUBLE PRECISION NOT NULL,
            sisa_kuota_berjalan DOUBLE PRECISION NOT NULL,
            geom GEOMETRY(Polygon, 4326) NOT NULL,
            h3_indices VARCHAR[],
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)
    op.execute("CREATE INDEX idx_plots_geom ON plots USING GIST (geom);")
    op.execute("CREATE INDEX idx_plots_h3_gin ON plots USING GIN (h3_indices);")

    # 5. Master Tabel Audit Ledger Terpartisi
    op.execute("""
        CREATE TABLE audit_ledger (
            id UUID NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            plot_id VARCHAR NOT NULL,
            dds_reference VARCHAR NOT NULL,
            compliance_status VARCHAR NOT NULL,
            digital_seal VARCHAR NOT NULL,
            payload_json TEXT NOT NULL,
            PRIMARY KEY (id, created_at)
        ) PARTITION BY RANGE (created_at);
    """)

    # 6. Sub-Tabel Partisi Kuartal
    op.execute("""
        CREATE TABLE audit_ledger_2026_q2 PARTITION OF audit_ledger
            FOR VALUES FROM ('2026-04-01 00:00:00+00') TO ('2026-07-01 00:00:00+00');
    """)
    op.execute("""
        CREATE TABLE audit_ledger_2026_q3 PARTITION OF audit_ledger
            FOR VALUES FROM ('2026-07-01 00:00:00+00') TO ('2026-10-01 00:00:00+00');
    """)
    op.execute("""
        CREATE TABLE audit_ledger_2026_q4 PARTITION OF audit_ledger
            FOR VALUES FROM ('2026-10-01 00:00:00+00') TO ('2026-12-31 23:59:59+00');
    """)

    # 7. Indeks Ledger
    op.execute("CREATE INDEX idx_audit_ledger_plot_created ON audit_ledger (plot_id, created_at);")
    op.execute("CREATE INDEX idx_audit_ledger_dds_created ON audit_ledger (dds_reference, created_at);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS audit_ledger CASCADE;")
    op.execute("DROP TABLE IF EXISTS plots CASCADE;")
    op.execute("DROP TABLE IF EXISTS kawasan_hutan_prioritas_3 CASCADE;")
    op.execute("DROP TABLE IF EXISTS hgu_prioritas_1 CASCADE;")