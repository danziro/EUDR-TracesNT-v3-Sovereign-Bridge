# Sovereign RegTech Protocol (SRP) — Spatio-Temporal Trust Oracle
**End-to-End Enterprise Architecture for EUDR 2023/1115 & 2025/2650 Compliance**

Sistem gerbang kepatuhan berdaulat (*Sovereign Compliance Gateway*) terpadu yang memadukan **Kecerdasan Buatan Geospasial (GeoAI)**, **Rekayasa Data Terdistribusi (Kafka/PostGIS)**, dan **Kriptografi Pembuktian Asimetris (ZK-SNARKs & eIDAS)**.

Protokol ini dirancang secara khusus untuk menyelesaikan benturan yurisdiksi (*jurisdictional deadlock*) antara kedaulatan data hukum agraria Indonesia dengan tuntutan transparansi pabean **TRACES NT Uni Eropa**.

### 🛡️ KARTU IDENTITAS PROTOKOL (*SOVEREIGN COMPLIANCE CARD*)

```text
┌────────────────────────────────────────────────────────────────────────┐
│  PROTOCOL IDENTITY     : Sovereign RegTech Protocol (SRP) v3.0         │
│  OPERATOR IDENTIFIER   : ID-EORI-2026-SAWIT-INHU-01                    │
│  REGULATORY JURISD.    : Regulation (EU) 2023/1115 & (EU) 2025/2650    │
│  API SCHEMA & VERSION  : TRACES NT v3 M2M SOAP-to-REST Spec v2026.2    │
│  SOVEREIGN BARRIER     : zk-SNARKs Groth16 (Secp256r1 Elliptic Curve)  │
│  CRYPTOGRAPHIC ENGINE  : eIDAS Qualified Electronic Timestamp (RFC 3161)│
│  GEOSPATIAL SCOPE      : Indragiri Hulu, Riau, Republic of Indonesia   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ⚖️ THE GEOPOLITICAL DEADLOCK: MENGAPA PROTOKOL INI DIBANGUN?

Per Juni 2026, eksportir skala *enterprise* hingga *menengah* berada di persimpangan hukum internasional yang kritis. Komisi Eropa (EUDR) mewajibkan penyerahan koordinat poligon mentah (*raw GeoJSON*) untuk setiap kargo ekspor. Namun, Undang-Undang Agraria Nasional Indonesia melarang keras pembagian batas spasial Hak Guna Usaha (HGU) ke server asing demi alasan pertahanan dan rahasia negara.

**Sovereign RegTech Protocol (SRP)** menyelesaikan kebuntuan ini dengan memisahkan **kebenaran fisik bumi (*Atoms*)** dari **kepatuhan administratif (*Bits*)** menggunakan arsitektur hibrida dua mesin.

---

## 🏗️ MONOREPO ARCHITECTURE: ATOMS-TO-BITS CYBERNETIC LOOP

Repositori ini adalah sebuah monorepo yang menaungi dua mesin utama (*Dual-Engine*). Keduanya bekerja secara asinkron untuk menjamin *Silsilah Pengawasan* (*Chain-of-Custody*) yang tidak terputus dari satelit di luar angkasa hingga ke server bea cukai di Eropa.

### 1. The Atoms Engine: `EarthObservation_Pipeline/`
Mesin hulu yang mengolah data fisika satelit untuk membuktikan bahwa lahan bebas deforestasi tanpa bias.
* **Radar-Optical Fusion:** Mengawinkan Sentinel-2 (Optik P10 Reducer) dan Sentinel-1 (Radar RTC) untuk menembus tutupan awan tebal di wilayah tropis.
* **AI Delineation & LSMA:** Menggunakan model fondasi *Prithvi-v2* & *SAM 3* untuk segmentasi poligon, dan *Sub-Pixel Spectral Mixture Analysis* untuk mendeteksi *Non-Photosynthetic Vegetation* (NPV/Kayu Mati).
* **Phenology Fingerprinting:** Menganalisis siklus tanam ulang (*replanting*) menggunakan algoritma *Dynamic Time Warping (DTW)* pada kurva sigmoidal untuk membantah *false-positive* dari satelit JRC Eropa.

### 2. The Bits Engine: `EUDR_Backend_API/`
Mesin hilir yang mengunci fakta fisik menjadi transaksi finansial dan kriptografis yang sah secara hukum.
* **Yield Verification Engine (YVE) & ACID Quota:** Mengubah poligon spasial menjadi batas kuota panen biologis secara dinamis. Mendebit kuota secara transaksional di **PostGIS** untuk mencegah eksploitasi koordinat (*Double-Spending/Laundering*).
* **Sovereign ZK-Bridge:** Membangkitkan bukti matematika *Groth16* di server domestik. Eropa memverifikasi kepatuhan secara instan tanpa pernah melihat koordinat fisik HGU asli.
* **SOAP-to-REST Interoperability:** Mengonversi data JSON-LD lokal menjadi amplop kaku XML/SOAP v3 secara asinkron untuk menembus gerbang pabean TRACES NT warisan (*legacy system*).

---

## 📂 PANDUAN NAVIGASI REPOSITORI (DIRECTORY MAP)

Repositori ini ditata secara ketat untuk memfasilitasi audit oleh tim *Engineering* maupun *Legal Compliance*.

```text
Sovereign-SpatioTemporal-Verification-Protocol/
│
├── deliverables_sample/               # [FOLDER CONTOH OUTPUT STERIL]
│   ├── Cleaned_EUDR_Polygons_2026.geojson   # Poligon 2D steril hasil sanitasi topologi spasial (RFC 7946).
│   ├── DDS_EUDR-INHU-001_40437...json       # Berkas Due Diligence Statement (JSON-LD) yang siap diumpan ke Uni Eropa.
│   ├── EUDR_eIDAS_Timestamp.tsr             # Token stempel waktu biner asli (ASN.1 DER-encoded RFC 3161).
│   └── EUDR_Final_Certificate_2026.json     # Bundel sertifikat final (evidentiary cluster) berisi JSON-LD + ZK Proof.
│
├── EarthObservation_Pipeline/         # [THE ATOMS ENGINE] Pipa pengolahan fisika bumi hulu
│   ├── GeoAICode_Simulation.ipynb           # Notebook interaktif fusi radar/optis, segmentasi, dan analisis runtun waktu.
│   └── README_EarthObservation.md           # Panduan eksekusi pipeline satelit di lingkungan cloud/Google Colab.
│
├── EUDR_Backend_API/                  # [THE BITS ENGINE] API, Pipa Event-Driven & database Transaksional
│   ├── alembic/                             # Skrip kontrol migrasi skema database relasional spasial
│   │   ├── versions/                        # Berkas mutasi struktur tabel database fisik (DDL)
│   │   │   ├── c209c1826454_baseline...py   # Migrasi PostGIS (Setup tabel HGU, Hutan Lindung, dan Partisi Range).
│   │   │   └── fb0ddd0c8aea_create_sec...py # Migrasi pembentukan Secure Personal Data Vault (GDPR Compliance).
│   │   ├── env.py                           # Konektor asinkron engine SQLAlchemy untuk migrasi skema database.
│   │   ├── README                           # Penjelasan alur migrasi database.
│   │   └── script.py.mako                   # Templat penulisan berkas revisi migrasi.
│   │
│   ├── app/                                 # Logika inti layanan mikroservis FastAPI
│   │   ├── services/                        # Mesin pemrosesan kepatuhan dan audit transaksional
│   │   │   ├── __init__.py
│   │   │   ├── audit_readiness.py           # Mesin audit kesiapan: penelusuran lineage, validasi akurasi, dan anti-tamper.
│   │   │   ├── cryptography.py              # Penyegel kriptografi eIDAS: pengiriman kueri biner ASN.1 ke QTSP Eropa.
│   │   │   ├── fallback_manager.py          # Pengendali darurat: Playwright RPA bot dan dynamic split shipment.
│   │   │   ├── flow_modeling.py             # Pemodelan transien neraca massa CSTR & aktuasi register PLC pabrik.
│   │   │   ├── g2g_gateway.py               # Handshaker ZK-SNARKs dasbor nasional Indonesia (NDI/Kepmenko 178/2024).
│   │   │   ├── geo_audit.py                 # Analisis spasial: sanitasi topologi Shapely dan polyfill indeks Uber H3.
│   │   │   ├── ingestion.py                 # Pekerja ingesti: ekstraksi EXIF, OpenCV thresholding, dan parser OCR LLM.
│   │   │   ├── kafka_manager.py             # Orkestrator Kafka: dual-worker (Vision & Spatial) dan Dead-Letter Queue.
│   │   │   ├── traces_gateway.py            # Penghubung pabean sekunder.
│   │   │   ├── traces_m2m.py                # Kompilator payload semantik JSON-LD TRACES-NT v2026.2.
│   │   │   ├── vault.py                     # Brankas data pribadi GDPR: enkripsi Fernet AES-256 dan Key Shredding.
│   │   │   └── zkv_engine.py                # Sirkuit ZK-Proof Groth16 (P-256): Prover & Verifier asimetris.
│   │   │
│   │   ├── __init__.py
│   │   ├── database.py                      # Konfigurasi asinkron engine SQLAlchemy & database connection pooling.
│   │   ├── logger.py                        # Konfigurasi Structured JSON Logging menggunakan structlog.
│   │   ├── main.py                          # Endpoint API, FastAPI entrypoint, dan kontrol daur hidup kontainer (lifespan).
│   │   ├── models.py                        # Model database deklaratif relasional spasial PostGIS.
│   │   └── schemas.py                       # Skema validasi tipe data masukan menggunakan Pydantic.
│   │
│   ├── docker/                              # Konfigurasi isolasi lingkungan pengapalan sistem
│   │   ├── Dockerfile                       # Multi-stage production build untuk optimalisasi ukuran kontainer API.
│   │   └── init-db.sql                      # Inisialisasi awal ekstensi spasial PostGIS dan UUID OS-SP.
│   │
│   ├── venv/                                # Virtual Environment lokal Python (Diabaikan oleh Git via .gitignore).
│   ├── .env                                 # Kunci rahasia & API credential sistem lokal (Diabaikan oleh Git).
│   ├── .env.example                         # Templat variabel konfigurasi runtime yang aman dibagikan publik.
│   ├── alembic.ini                          # Konfigurasi parameter migrasi Alembic.
│   ├── docker-compose.yml                   # Orkestrator multi-kontainer (PostGIS, Redis, Kafka, Neo4j, FastAPI).
│   ├── national_g2g_ledger.jsonl            # Buku besar rahasia nasional domestik (Diabaikan oleh Git).
│   └── README_BACKEND.md                    # Panduan teknis konfigurasi, inisialisasi, dan pengujian Bits Engine.
│
├── eudr_sdk/                          # [PUBLIC INTEGRATION GATEWAY] Modul integrasi klien BUMN
│   ├── __init__.py
│   ├── eidas_sealer.py                      # SDK klien untuk request tanda tangan stempel waktu QTSP Eropa (eIDAS).
│   ├── schemas.py                           # Pydantic schema pemetaan komoditas (NIB, HGU, ISPO).
│   ├── soap_wrapper.py                      # Konverter taktis penulisan JSON-LD hulu menjadi SOAP XML v3 pabean Eropa [2.1.5, 2.3.1].
│   └── traces_client.py                     # Klien transmisi asinkron M2M ke gerbang pabean TRACES NT [41].
│
├── .gitignore                         # Kebijakan penyaringan berkas rahasia dan sampah sistem sebelum push Git.
├── README.md                          # [THE GRAND MANIFESTO] Cetak biru arsitektur hulu-hilir komprehensif.
└── requirements.txt                   # Kunci dependensi pustaka Python global berstandar produksi.
```

---

## 🚀 GETTING STARTED (CARA MENJALANKAN SISTEM)

Karena ini adalah arsitektur Monorepo, instruksi instalasi dan eksekusi dipisahkan berdasarkan domain keahlian:

1. **Data Scientist / GIS Engineer:** 
   Silakan menuju ke direktori `EarthObservation_Pipeline/` dan baca `README_EarthObservation.md` untuk menjalankan simulasi fusi citra satelit di Google Colab/Jupyter.
2. **Backend / DevOps Engineer:** 
   Silakan menuju ke direktori `EUDR_Backend_API/` dan baca `README_BACKEND.md` untuk memutar infrastruktur *Event-Driven* (PostGIS, Kafka, Redis, FastAPI) menggunakan Docker Compose.

---

## 🛡️ HAK PENGHAPUSAN DATA (GDPR PASAL 17 COMPLIANCE)

Sistem ini menyelesaikan benturan antara kewajiban simpan data audit 5 tahun (EUDR) dan hak penghapusan data (GDPR). Identitas asli petani dienkripsi dengan **AES-256 (Fernet)** di dalam `Secure Personal Data Vault`. 
Jika ada tuntutan hukum penghapusan data, sistem mengeksekusi *Key Shredding*. Silsilah transaksi ekspor di buku besar (*ledger*) tetap utuh untuk audit Eropa, sementara data identitas penyuplai musnah secara kriptografis demi mematuhi privasi Eropa.

---

## ⚖️ BATAS LIABILITAS HUKUM & SLA (*INDEMNITY CAP*)

**PERNYATAAN PENAFIAN (DISCLAIMER):**
*Sovereign RegTech Protocol (SRP)*, termasuk model *Earth Observation AI*, diposisikan secara mutlak sebagai **Sistem Pendukung Keputusan (*Decision-Support System/DSS*)**. 

Penyedia arsitektur dan penulis repositori ini **dibebaskan secara mutlak** dari segala bentuk tanggung jawab hukum (*Strict Liability*), gugatan kerugian konsekuensial, penyitaan kontainer komoditas di pelabuhan Eropa, atau denda administratif pabean yang dijatuhkan oleh otoritas kepabeanan Uni Eropa akibat galat operasional perangkat lunak (*software bugs*), *false positive* klasifikasi satelit, maupun perubahan regulasi sepihak dari Komisi Eropa. Segala bentuk implementasi kode di lingkungan produksi komersial berada di bawah risiko dan kewajiban entitas pengguna (*Enterprise Operator*) sepenuhnya.

---