import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# FIXED: Default fallback mengarah ke 'db' (bukan localhost) untuk menjamin koneksi internal Docker
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://eudr_admin:secure_password_2026@db:5432/geoai_eudr_db"
)

# Engine asinkron untuk performa konkurensi tinggi
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Session factory
SessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

# Dependency injection untuk FastAPI
async def get_db():
    async with SessionLocal() as session:
        yield session