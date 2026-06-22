import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# 1. Import Base model dan GeoAlchemy2 untuk dukungan tipe spasial
from app.models import Base
import geoalchemy2

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. Targetkan metadata dari model kita
target_metadata = Base.metadata

# 3. Ambil URL secara dinamis (fallback ke nama host Docker 'db')
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://eudr_admin:secure_password_2026@db:5432/geoai_eudr_db"
)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

def include_object(object, name, type_, reflected, compare_to):
    """
    Saringan Keamanan:
    Mencegah Alembic mencoba menghapus (dropping) tabel bawaan sistem PostGIS / Tiger Geocoder.
    """
    # Jika objek dideteksi dari database (reflected=True) tapi tidak kita definisikan 
    # di metadata models.py kita, abaikan sepenuhnya (jangan coba-coba di-drop!)
    if reflected and type_ == "table" and name not in target_metadata.tables:
        return False
        
    # Proteksi tambahan untuk tabel spasial referensi
    if type_ == "table" and name in ["spatial_ref_sys", "countysub_lookup", "zip_lookup"]:
        return False
        
    return True

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())