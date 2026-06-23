# Sovereign RegTech Protocol (SRP) — Spatio-Temporal Trust Oracle for Global Commodity Traceability

Sistem gerbang kepatuhan berdaulat (*Sovereign Compliance Gateway*) terpadu berbasis kecerdasan buatan geospasial (GeoAI), rekayasa data terdistribusi asinkron, dan kriptografi pembuktian tanpa pengungkapan (*Zero-Knowledge Proofs*). 

Protokol ini dirancang untuk menjembatani benturan yurisdiksi antara **Dasbor Nasional Indonesia (ID Connect)** dengan sistem **TRACES NT Uni Eropa** di bawah regulasi **EUDR 2023/1115** dan amandemen penangguhan **EUDR 2025/2650**. Sistem ini mengunci pembuktian fisik kelapa sawit (*Atoms*) hulu dan menyegelnya menjadi catatan audit administratif digital (*Bits*) hilir yang sah secara hukum di pelabuhan Eropa (*eIDAS Non-Repudiation*).

### 🛡️ KARTU IDENTITAS KEPATUHAN PROTOKOL (*SOVEREIGN COMPLIANCE CARD*)

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

## ⚖️ SEKSI 1: DILEMA GEOPOLITIK & SOLUSI KEDAULATAN DATA

### 1. Kebuntuan Diplomatik Jakarta vs. Brussel per Juni 2026
Komisi Eropa melalui regulasi EUDR mewajibkan pengunggahan koordinat poligon batas lahan komersial secara transaksional ke portal TRACES NT untuk setiap kargo ekspor. Sebaliknya, Undang-Undang Kedaulatan Data Nasional Indonesia (Kebijakan Satu Peta / *One Map Policy*) melarang keras pembagian batas spasial mentah HGU (*raw geolocation*) ke pihak asing demi alasan pertahanan nasional dan rahasia dagang agraria. Portal *ID Connect* milik PT Surveyor Indonesia dan BPDPKS sedang berjuang keras menjembatani kebuntuan transmisi ini.

**Dilema Direksi Eksportir:**
*   **Patuhi Aturan Uni Eropa (DDS Upload):** Mengekspos rahasia dagang agraria nasional ke pasar global dan menghadapi risiko tuntutan pidana kebocoran rahasia negara serta gugatan sengketa lahan lokal.
*   **Patuhi Hukum Indonesia (Sovereign Shield):** Kargo ditahan di pelabuhan Eropa, kapal disita, dan denda administratif hingga **4% dari total omset tahunan importir** berdasarkan ketentuan Pasal 25 EUDR.

---

## 🔐 SEKSI 2: ZERO-KNOWLEDGE PROOFS (ZKV) SEBAGAI SOLUSI BERDAULAT

SRP memecahkan benturan hukum internasional ini dengan menerapkan sirkuit **Zero-Knowledge Verification (ZKV) Groth16** di atas kurva eliptik **Secp256r1/ECDSA**.

```text
       [ PROVER: INDONESIA (G2G/NDI) ]                       [ VERIFIER: UNI EROPA (TRACES NT) ]
 ┌─────────────────────────────────────────┐               ┌───────────────────────────────────┐
 │ Private Input / Witness (w):            │               │ Public Input (x):                 │
 │ - Batas Lahan Raw HGU (Sangat Rahasia)  │               │ - Hash Batas Lahan (witness_hash) │
 │ - Peta Kawasan Hutan Lindung            │               │ - ID Transaksi Ekspor             │
 │ - Sertifikat Agraria Asli (BPN)         │               │ - Stempel Waktu (Timestamp)       │
 └────────────────────┬────────────────────┘               └─────────────────┬─────────────────┘
                      │                                                      │
                      ▼ (Evaluasi Sirkuit C(x,w))                            │
 ┌─────────────────────────────────────────┐                                 │
 │ Proving Key (PK):                       │                                 │
 │ (Secp256r1 Private Key)                 │                                 │
 └────────────────────┬────────────────────┘                                 │
                      │                                                      │
                      ▼ (Sign / Generate Proof)                              │
 ┌─────────────────────────────────────────┐                                 │
 │ Bukti Kriptografi Biner (π):            │ ── (Kirim bukti π & public input x) ──►
 │ - r, s (Signature) [Ukuran: ~300 Bytes] │                                 ▼
 └─────────────────────────────────────────┘               ┌───────────────────────────────────┐
                                                           │ Verifying Key (VK):               │
                                                           │ (Secp256r1 Public Key)            │
                                                           ├───────────────────────────────────┘
                                                           │ verify_zk_proof(pi, x) -> True/False
                                                           └───────────────────────────────────┘
                                                            * Brussel membuktikan kepatuhan lahan
                                                            * TANPA PERNAH MELIHAT BATAS LAHAN RAW!
```

Eksportir lokal membuktikan secara tertutup (*offline prover*) di server domestik BPN/Dasbor Nasional bahwa lahan mereka **Bebas Deforestasi** dan **Berada di dalam Batas Legal HGU**. Hasil pembuktian menghasilkan tanda tangan biner ($r, s$) yang ringkas ($\pi$) beserta input publik ($x$). 

Uni Eropa dapat memverifikasi kebenaran matematika pembuktian tersebut menggunakan *Verifying Key* ($VK$) tanpa pernah bisa merekonstruksi koordinat spasial HGU asli hulu, sehingga meloloskan *Union Reference Number* (URN) pabean secara sah tanpa kebocoran informasi.

---

## 🔄 SEKSI 3: CETAK BIRU ALIRAN DATA SIBER-FISIK (ATOMS-TO-BITS CYBERNETIC LOOP)

Protokol SRP bekerja sebagai pipa data satu arah (*unidirectional pipeline*) yang secara asinkron menyerap kebenaran fisik bumi (*Atoms*) di tingkat hulu, melakukan penyaringan anomali, mengonversinya menjadi graf silsilah logistik, dan menguncinya menjadi tanda tangan kriptografi biner (*Bits*) hilir yang siap diumpankan ke TRACES NT.

```text
                                  [ THE ATOMS ENGINE: PHYSICAL TRUTH ]
 ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ Copernicus CDSE Ingestion ──► S1/S2 Sensor Fusion ──► Prithvi-v2 Segmentasi ──► Shapely 2D Sanitasi│
 └────────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                      │
                                                      ▼ (Vektor Batas Lahan Steril WGS84)
                                  [ THE BITS ENGINE: CRYPTOGRAPHIC LEDGER ]
 ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ WhatsApp Webhook ──► Kafka Broker ──► PostGIS ACID Ledger ──► GDPR Fernet Vault ──► eIDAS TSA Sealer│
 └────────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                      │
                                                      ▼ (Evidentiary Cluster & .tsr biner)
                                  [ THE GATEWAY TRANSMISSION: COMPLIANCE ]
 ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                          TRACES NT OAuth 2.0 API Gateway ──► Union Reference Number (URN)               │
 └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

1.  **The Atoms Engine (Ground-Truth Generation):** Mengolah fusi citra satelit hulu bebas awan menggunakan superkomputer CDSE openEO API. Lahan disegmentasi secara presisi oleh model fondasi *Prithvi-v2* (adapter LoRA *Bio-Physical_Palm_Riau*) dan *SAM 3* untuk memproduksi poligon batas lahan. Poligon disterilisasi topologinya menggunakan toleransi jarak Douglas-Peucker 1.5 meter, dipangkas dari dimensi Z (murni 2D), dan dipaksa mematuhi aturan arah putaran cincin koordinat luar berlawanan jarum jam (CCW / Right-Hand Rule RFC 7946) guna menghindari penolakan oleh parser TRACES NT.
2.  **The Bits Engine (Verifiable Trust Ledger):** Mengamankan silsilah transaksi hulu berkecepatan tinggi secara non-blocking melalui pembagian antrean Apache Kafka. Poligon spasial dipolyfill menjadi grid hexagonal *Uber H3 Resolusi 11* yang dilindungi indeks *GIN (Generalized Inverted Index)* di tingkat database PostGIS untuk mempercepat kueri irisan spasial secepat $O(1)$. Mencegah penipuan koordinat berulang (*double-spending*) secara transaksional (ACID) melalui pemotongan saldo kuota berjalan *Yield Verification Engine (YVE)*. Identitas asli petani diisolasi menggunakan enkripsi simetris Fernet (AES-256) di dalam *Secure Personal Data Vault* yang mendukung fungsi penghancuran kunci (*Key Shredding*) untuk kepatuhan mutlak GDPR Pasal 17.
3.  **The Gateway Transmission (Cryptographic Non-Repudiation):** Mengompilasi payload Web Semantik JSON-LD TRACES NT versi `2026.2`. Menghitung sidik jari digital (SHA-256 Hash) dari payload tersebut dan mengirimkannya dalam format biner ASN.1 DER-encoded menuju server Qualified Trust Service Provider (QTSP) Eropa (eIDAS RFC 3161) untuk menyegel token stempel waktu digital `.tsr` biner yang sah secara hukum. Seluruh berkas pabean dikirim ke TRACES NT melalui jabat tangan asinkron OAuth 2.0 Client Credentials Flow untuk mengekstrak nomor rujukan pabean URN.

---

## 📂 SEKSI 4: PETA PANDUAN NAVIGASI MONOREPO (ANNOTATED REPOSITORY MAP)

Repositori terpadu (*Monorepo*) ini ditata secara ketat sesuai standar *enterprise-grade repository hygiene* guna memisahkan lingkungan kerja riset GeoAI dengan mikroservis produksi backend, sekaligus menyediakan etalase publik yang aman untuk audit independen:

```text
Sovereign-SpatioTemporal-Verification-Protocol/
│
├── deliverables_sample/               # [FOLDER CONTOH OUTPUT STERIL]
│   ├── Cleaned_EUDR_Polygons_2026.geojson   # Batas lahan steril 2D standar pabean (CCW).
│   ├── DDS_EUDR-INHU-001_40437...json       # Berkas Due Diligence Statement (JSON-LD) TRACES NT.
│   ├── EUDR_eIDAS_Timestamp.tsr             # Token stempel waktu biner QTSP asli (RFC 3161 DER).
│   └── EUDR_Final_Certificate_2026.json     # Bundel sertifikat final (evidentiary cluster) siap audit.
│
├── EarthObservation_Pipeline/         # [THE ATOMS ENGINE] Komputasi Spasial & GeoAI
│   ├── GeoAICode_Simulation.ipynb           # Notebook interaktif fusi radar/optis, SAM3, dan DTW hulu.
│   └── README_EarthObservation.md           # Panduan eksekusi pipeline satelit di lingkungan cloud/Colab.
│
├── EUDR_Backend_API/                  # [THE BITS ENGINE] API, Pipa Event-Driven & database Transaksional
│   ├── alembic/                             # Skrip kontrol migrasi skema database relasional PostGIS
│   │   ├── versions/                        # Berkas revisi mutasi struktur tabel (DDL)
│   │   │   ├── c209c1826454_baseline...py   # Migrasi PostGIS: Tabel HGU, Hutan, dan Range Partitions.
│   │   │   └── fb0ddd0c8aea_create_sec...py # Migrasi pembentukan Secure Personal Data Vault (GDPR).
│   │   ├── env.py                           # Konektor asinkron engine SQLAlchemy untuk migrasi database.
│   │   └── ...                              # Pendukung migrasi standar Alembic
│   ├── app/                                 # Logika utama layanan mikroservis FastAPI
│   │   ├── services/                        # Mesin pemrosesan kepatuhan hulu-hilir
│   │   │   ├── audit_readiness.py           # Mesin audit kesiapan: lineage backtrack, akurasi model, anti-tamper.
│   │   │   ├── cryptography.py              # Penyegel kriptografi eIDAS: kueri biner ASN.1 ke QTSP.
│   │   │   ├── fallback_manager.py          # Pengendali darurat: Playwright RPA bot dan dynamic split shipment.
│   │   │   ├── flow_modeling.py             # Pemodelan transien reaktor CPO (CSTR) & aktuasi PLC pabrik.
│   │   │   ├── g2g_gateway.py               # Handshaker ZK-SNARKs dasbor nasional Indonesia (NDI/Kepmenko 178/2024) [96].
│   │   │   ├── geo_audit.py                 # Analisis spasial: sanitasi topologi Shapely & Uber H3 indexing.
│   │   │   ├── ingestion.py                 # Pekerja ingesti: EXIF extractor, OpenCV threshold, & parser LLM.
│   │   │   ├── kafka_manager.py             # Orkestrator Kafka: dual-worker (Vision & Spatial) & DLQ.
│   │   │   ├── traces_m2m.py                # Kompilator payload semantik JSON-LD TRACES-NT v2026.2.
│   │   │   ├── vault.py                     # Brankas data GDPR: enkripsi Fernet AES-256 & Key Shredding.
│   │   │   └── zkv_engine.py                # Sirkuit ZK-Proof Groth16 (P-256): Prover & Verifier asimetris.
│   │   ├── database.py                      # Konfigurasi asinkron engine SQLAlchemy & database pooling.
│   │   ├── logger.py                        # Konfigurasi Structured JSON Logging menggunakan structlog.
│   │   ├── main.py                          # Endpoint API, FastAPI entrypoint, dan asinkron lifespan.
│   │   ├── models.py                        # Model database deklaratif relasional spasial PostGIS.
│   │   └── schemas.py                       # Skema validasi tipe data masukan menggunakan Pydantic.
│   ├── docker/                              # Konfigurasi isolasi lingkungan pengapalan sistem
│   │   ├── Dockerfile                       # Multi-stage production build untuk optimasi ukuran kontainer.
│   │   └── init-db.sql                      # Inisialisasi awal ekstensi spasial PostGIS dan UUID OS-SP.
│   ├── .env.example                         # Templat variabel konfigurasi runtime yang aman dibagikan publik.
│   ├── alembic.ini                          # Konfigurasi parameter migrasi Alembic.
│   ├── docker-compose.yml                   # Orkestrator multi-kontainer (PostGIS, Redis, Kafka, Neo4j, FastAPI).
│   └── README_BACKEND.md                    # Panduan teknis konfigurasi, inisialisasi, dan pengujian API.
│
├── eudr_sdk/                          # [PUBLIC INTEGRATION GATEWAY] Modul integrasi
│   ├── eidas_sealer.py                      # SDK klien untuk request tanda tangan stempel waktu QTSP eIDAS.
│   ├── schemas.py                           # Pydantic schema pemetaan komoditas (NIB, HGU, ISPO).
│   ├── soap_wrapper.py                      # Konverter taktis penulisan JSON-LD hulu menjadi SOAP XML v3 pabean Eropa [2.1.5, 2.3.1].
│   └── traces_client.py                     # Klien transmisi asinkron M2M ke gerbang pabean TRACES NT.
│
├── .gitignore                         # Kebijakan penyaringan berkas rahasia dan sampah kompilasi.
├── README.md                          # [THE GRAND MANIFESTO] Cetak biru arsitektur komprehensif (File Ini).
└── requirements.txt                   # Kunci dependensi pustaka Python global berstandar produksi.
```

---

## 🚦 SEKSI 5: GERBANG ONBOARDING BERBASIS PERSONA (TECHNICAL ROUTING GATES)

Untuk memitigasi hambatan kognitif (*cognitive load*) bagi para pengevaluasi teknis, instruksi operasional di dalam repositori ini dipisahkan secara kaku berdasarkan domain keahlian. 

Silakan pilih gerbang masuk yang sesuai dengan spesifikasi peran Anda untuk memulai proses audit:

### 🛰️ GERBANG 1: Untuk Data Scientist / GIS Specialist
Jika tanggung jawab Anda berfokus pada analisis spasial hulu, pembuktian bio-fisik tutupan lahan, fusi sensor satelit, dan model fondasi segmentasi AI:
*   **Workspace Fokus:** `EarthObservation_Pipeline/`
*   **Spesifikasi Teknis:** CDSE openEO APIs, Sentinel-1/2 RTC, IBM/NASA *Prithvi-v2* LoRA, SAM 3, sub-pixel LSMA (NPV), dan Dynamic Time Warping (DTW).
*   **Tautan Panduan Kerja:** [Buka Panduan Komputasi Spasial (README_EarthObservation.md)](EarthObservation_Pipeline/README_EarthObservation.md)

### 💻 GERBANG 2: Untuk DevOps / Backend / Security Architect
Jika tanggung jawab Anda berfokus pada keandalan pipa data berkecepatan tinggi, kueri database spasial, keamanan data pribadi (GDPR), dan penyegelan kriptografi:
*   **Workspace Fokus:** `EUDR_Backend_API/`
*   **Spesifikasi Teknis:** FastAPI Async, Apache Kafka Decoupling, PostGIS GIN H3 Grid (Resolusi 11), range partitioning SQL, Fernet AES-256 GDPR Vault, dan eIDAS Qualified Timestamping (RFC 3161).
*   **Tautan Panduan Kerja:** [Buka Panduan Mikroservis API (README_BACKEND.md)](EUDR_Backend_API/README_BACKEND.md)

---

## 🔒 SEKSI 6: VERIFIKASI KUSTODI BUKTI DIGITAL (STERILE DELIVERABLES AUDIT)

Protokol SRP menganut asas transparansi mutlak yang dapat dibuktikan secara mandiri. Kami menyediakan direktori khusus `deliverables_sample/` sebagai *brankas bukti steril* (*sterile sandbox*). 

Otoritas pabean Eropa dan auditor eksternal dapat langsung memvalidasi keabsahan rangkaian silsilah (*chain-of-custody*) kepatuhan ekspor kami tanpa harus mengakses database operasional hilir:

1.  **`Cleaned_EUDR_Polygons_2026.geojson` (Master Vector):** Berkas batas lahan tersterilisasi 2D standar WGS-84 (EPSG:4326). Poligon telah disederhanakan dengan toleransi Douglas-Peucker 1.5 meter dan cincin geometri luar telah dipaksa berputar berlawanan arah jarum jam (CCW) sesuai spesifikasi mutlak pabean Eropa.
2.  **`DDS_EUDR-INHU-001_EUDR-2026-40437...json` (DDS Payload JSON-LD):** Pernyataan Uji Tuntas (DDS) resmi berstandar Web Semantik JSON-LD spesifikasi v2026.2. Payload ini mengunci kode komoditas CPO *Combined Nomenclature* 8-digit **CN-Code `15111090`**, menyematkan metadata sertifikasi ISPO hulu, dan menyuntikkan koordinat GeoJSON steril di atas.
3.  **`EUDR_eIDAS_Timestamp.tsr` (Certified Timestamp Token):** Berkas biner stempel waktu kaku (*Qualified Electronic Timestamp*) berstandar RFC 3161 DER-encoded. Berkas biner asli ini ditandatangani langsung oleh Qualified Trust Service Provider (QTSP) resmi Eropa (DigiCert).
4.  **`EUDR_Final_Certificate_2026.json` (Evidentiary Cluster):** Sertifikat digital final yang merangkai hash SHA-256 GeoJSON, hash GeoTIFF satelit, metadata stempel waktu, dan rujukan ke token `.tsr` menjadi satu kesatuan dokumen pembuktian hukum yang kebal manipulasi.

### 🛠️ Protokol Verifikasi Forensik TSR Mandiri

Para auditor dapat menjalankan perintah OpenSSL standar industri berikut pada terminal lokal untuk membuktikan bahwa data spasial dan transaksi pabean di dalam repositori ini telah disegel secara sah oleh otoritas waktu global terpercaya:

```bash
# Pindah ke direktori bukti steril
cd deliverables_sample/

# Eksekusi parsing biner ASN.1 DER TSR terhadap jam atom global
openssl ts -reply -in EUDR_eIDAS_Timestamp.tsr -text
```

---

## ⚖️ SEKSI 7: BATAS LIABILITAS HUKUM & KONTRAK JASA (SLA INDEMNITY CAP)

Untuk mengamankan kepentingan komersial, operasional, dan finansial dari penyedia solusi teknologi *Sovereign RegTech Protocol (SRP)* terhadap risiko keuangan berat akibat yurisdiksi tanggung jawab mutlak (*Strict Liability*) pabean asing, kontrak kerja sama teknis diatur secara ketat oleh klausul perlindungan hukum berikut:

### 1. Status Hukum Sistem Pendukung Keputusan (*Decision-Support System*)

Sistem ini diklasifikasikan murni sebagai **Sistem Pendukung Keputusan (*Decision-Support System* - DSS)**. Hasil klasifikasi semantik kecerdasan buatan, visualisasi peta satelit hulu, pembatasan kuota panen, dan penentuan status kepatuhan ditujukan untuk membantu operator menyusun bukti pembelaan teknis kepabeanan (*customs technical dossier*). 

Layanan ini tidak bertindak sebagai jaminan kelolosan mutlak bebas galat, nasihat hukum formal, atau penjamin bebas sanksi pabean eksternal. Keputusan akhir atas kelolosan ekspor komoditas kelapa sawit sepenuhnya berada di bawah otoritas pabean Uni Eropa dan instansi bea cukai negara anggota terkait.

### 2. Batas Ganti Rugi Finansial Maksimal (*SLA Indemnity Cap*)

Nilai ganti rugi maksimal (*liability cap*) yang wajib dibayarkan oleh penyedia layanan jasa teknologi kepada klien atas setiap tuntutan hukum, klaim kerugian, investigasi pabean, atau kegagalan kepatuhan geospasial hulu dibatasi secara mutlak **maksimal setara dengan total biaya layanan (*service fee*) yang dibayarkan secara riil oleh klien dalam kurun waktu 12 bulan terakhir** sebelum terjadinya peristiwa tuntutan hukum terkait.

### 3. Pengecualian Kerugian Konsekuensial (*Exclusion of Consequential Damages*)

Penyedia jasa teknologi dibebaskan secara mutlak, penuh, dan tanpa pengecualian dari segala bentuk tuntutan ganti rugi atas:
*   Kerugian tidak langsung (*indirect damages*).
*   Kerugian konsekuensial (*consequential damages*) berupa kehilangan potensi pasar, hilangnya keuntungan bisnis (*lost profits*), penolakan pengapalan sepihak di pelabuhan tujuan, penyitaan kapal pengangkut komoditas fisik, atau denda administratif pabean Uni Eropa sebesar 4% omset tahunan importir berdasarkan Pasal 25 EUDR akibat adanya kesalahan penafsiran data spasial atau kegagalan integrasi M2M TRACES NT.