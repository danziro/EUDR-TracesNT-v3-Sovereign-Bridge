import uuid
from sqlalchemy import Column, String, Float, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.database import Base
from sqlalchemy import Column, String, Float, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from geoalchemy2 import Geometry
from app.database import Base

class Plot(Base):
    """
    Tabel penyimpanan batas lahan (Poligon) petani swadaya/korporasi.
    Dilengkapi kolom 'sisa_kuota_berjalan' untuk mencegah penipuan kuota panen [2650].
    """
    __tablename__ = "plots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plot_id = Column(String, unique=True, index=True, nullable=False)
    farmer_name = Column(String, nullable=False)
    nib = Column(String, nullable=False)
    commodity = Column(String, default="Oil Palm", nullable=False)
    area_ha = Column(Float, nullable=False)
    annual_quantity_estimate_mt = Column(Float, nullable=False)
    sisa_kuota_berjalan = Column(Float, nullable=False)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326, spatial_index=True), nullable=False)
    
    # Kolom Array untuk menyimpan Uber H3 Hexagon IDs (Resolusi 11)
    h3_indices = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Buat GIN Index agar pencarian irisan array sangat cepat
Index('idx_plots_h3_gin', Plot.h3_indices, postgresql_using='gin')

class HGUPrioritas1(Base):
    """
    Tabel Referensi Spasial Hak Guna Usaha (HGU) sebagai Prioritas I Hukum Nasional [1115].
    Peta ini dilindungi undang-undang kedaulatan data domestik (zk-SNARKs Prover).
    """
    __tablename__ = "hgu_prioritas_1"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nomor_sertifikat = Column(String, unique=True, index=True, nullable=False)
    pemegang_hak = Column(String, nullable=False)
    luas_sertifikat_ha = Column(Float, nullable=False)
    
    # Geometri MultiPolygon (Standard WGS84 - EPSG:4326)
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326, spatial_index=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class KawasanHutanPrioritas3(Base):
    """
    Tabel Referensi Spasial Kawasan Hutan Lindung/Konservasi Nasional (Prioritas III Hukum) [1115].
    Jika lahan petani masuk ke wilayah ini tanpa didasari HGU, sistem otomatis melakukan pemotongan (Clipping).
    """
    __tablename__ = "kawasan_hutan_prioritas_3"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nama_kawasan = Column(String, nullable=False)
    fungsi_hutan = Column(String, nullable=False) # Contoh: Hutan Produksi Terbatas (HPT), Hutan Lindung (HL)
    sk_menhut = Column(String, nullable=True) # Nomor Surat Keputusan Kementerian LHK
    
    # Geometri MultiPolygon (Standard WGS84 - EPSG:4326)
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326, spatial_index=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLedger(Base):
    """
    Log Transaksi Audit Kepatuhan EUDR yang diamankan untuk audit minimal 5 tahun (Pasal 11 & 12) [2650].
    Dipersiapkan untuk Table Partitioning berbasis range waktu (Waktu Pengajuan).
    """
    __tablename__ = "audit_ledger"

    # Pada database terpartisi PostgreSQL, kolom partisi waktu (created_at) 
    # wajib menjadi bagian dari Composite Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), primary_key=True, server_default=func.now())
    
    plot_id = Column(String, nullable=False)
    dds_reference = Column(String, nullable=False) # URN dari TRACES NT
    compliance_status = Column(String, nullable=False) # COMPLIANT / NON-COMPLIANT
    digital_seal = Column(String, nullable=False) # Hash SHA-256 dokumen spasial + metadata
    payload_json = Column(String, nullable=False) # Payload JSON-LD asli

# Pembuatan Indeks Pencarian Temporal untuk Data Lineage Back-tracking cepat (5 Years Retention)
Index('idx_audit_ledger_plot_created', AuditLedger.plot_id, AuditLedger.created_at)
Index('idx_audit_ledger_dds_created', AuditLedger.dds_reference, AuditLedger.created_at)

class SecurePersonalDataVault(Base):
    """
    Secure Token Vault (GDPR Compliance Table) [89].
    Menyimpan enkripsi data pribadi petani secara terisolasi dari tabel audit utama.
    """
    __tablename__ = "secure_personal_data_vault"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Token penhubung searah untuk referensi silang dari tabel plots/ledger
    association_token = Column(String, unique=True, index=True, nullable=False)
    
    # Nilai PII terenkripsi secara asimetris/simetris (AES-256)
    encrypted_farmer_name = Column(String, nullable=False)
    encrypted_nib = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())