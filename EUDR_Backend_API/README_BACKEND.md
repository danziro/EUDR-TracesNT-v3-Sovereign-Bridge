# API Kepatuhan Pabean EUDR & Mesin Kriptografi Hilir (The Bits Engine)

Layanan backend terdistribusi asinkron skala *enterprise* berbasis **FastAPI**, **Apache Kafka**, dan **PostGIS**. Layanan ini bertindak sebagai **The Bits Engine** dalam *Sovereign RegTech Protocol (SRP)*, bertanggung jawab untuk mengamankan silsilah pengapalan, melakukan verifikasi batas legalitas agraria, membatasi kuota ekspor secara biologis, menyegel berkas pabean berstandar eIDAS, serta mendistribusikan berkas kepatuhan ke pabean Eropa (TRACES NT).

---

## 🏗️ ARSITEKTUR LAYANAN & DISTRIBUSI KONTRAK

Layanan ini dirancang menggunakan arsitektur hibrida *Event-Driven* untuk memisahkan proses komputasi berat (pemrosesan gambar/OCR) dari penulisan transaksional database yang sensitif.

```text
                               ┌─────────────────────────┐
                               │   WhatsApp Webhook API  │
                               └────────────┬────────────┘
                                            │ (FastAPI HTTP 202)
                                            ▼
                             ┌─────────────────────────────┐
                             │ Apache Kafka Ingestion Loop │
                             └──────────────┬──────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼ (event.raw_ingestion)                         ▼ (event.geo_validation)
      ┌───────────────────────────┐                   ┌───────────────────────────┐
      │   Worker 1 (Vision/OCR)   │                   │  Worker 2 (Spatial/ACID)  │
      ├───────────────────────────┤                   ├───────────────────────────┤
      │ - Metadata EXIF GPS       │                   │ - Shapely 2D Sanitization │
      │ - OpenCV Adaptive Threshold │                   │ - H3 Ind indeks hexagonal │
      │ - EasyOCR Extraction      │                   │ - Multi-layer PostGIS     │
      │ - LLM Parser (Gemini/GPT) │                   │ - YVE & ACID Quota Ledger │
      │                           │                   │ - PII AES-256 Vaulting    │
      └─────────────┬─────────────┘                   └─────────────┬─────────────┘
                    │                                               │
                    ▼ (Picu jika gagal/deviasi >100m)               ▼ (Selesai Audit)
      ┌───────────────────────────┐                   ┌───────────────────────────┐
      │  Dead-Letter Queue (DLQ)  │                   │ Immutable Audit Ledger    │
      └───────────────────────────┘                   └───────────────────────────┘
```

---

## 🗂️ SPESIFIKASI MODUL SERVICES (THE CORE BITS)

Seluruh logika operasi silsilah kepatuhan diatur di dalam sub-direktori `app/services/`:

### 1. `ingestion.py` — Ingesti Citra Spasial & Forensik EXIF
*   **Forensik Metadata Geospasial:** Mengekstrak lintang (*latitude*), bujur (*longitude*), dan tanggal akuisisi foto secara langsung dari biner EXIF gambar yang dikirim petani hulu.
*   **Penyaringan Deviasi Lokasi:** Menghitung jarak Haversine secara matematis antara koordinat klaim petani dengan koordinat GPS fisik foto. Jika jarak deviasi $> 100$ meter, transaksi ekspor dibatalkan seketika dan dilempar ke topik Dead-Letter Queue (DLQ) untuk karantina manual.
*   **Computer Vision & OCR Parsing:** Menjalankan pra-pemrosesan citra menggunakan OpenCV *Adaptive Thresholding* untuk kontras maksimal, diikuti penarikan teks nota timbang secara dinamis menggunakan mesin *EasyOCR* (Lazy Loading) dan parsing JSON semantik menggunakan *LLM Parser (Gemini-1.5-Flash / GPT-3.5)*.

### 2. `geo_audit.py` — Sanitasi Topologi Spasial & PostGIS Matrix
*   **Sanitasi Geometri Shapely:** Menerima koordinat mentah, meluruskan geometri yang melilit/tidak valid (*self-intersection*) secara otonom melalui operasi `make_valid`, menyederhanakan titik simpul menggunakan algoritma Douglas-Peucker dengan toleransi ketat 1.5 meter, serta memaksa dimensi menjadi murni 2D sesuai standar GeoJSON RFC 7946.
*   **Kueri Spasial Multilapis PostGIS:** Menjalankan kueri database relasional spasial native untuk menguji irisan poligon terhadap Kawasan Hutan Lindung (Prioritas III) dan Hak Guna Usaha (Prioritas I).
*   **Auto-Clipping System:** Jika terdeteksi tumpang tindih kawasan hutan lindung di luar jaminan HGU yang sah, sistem secara otomatis mengeksekusi operasi pemotongan (*ST_Difference*) dengan penambahan area penyangga (*buffer*) aman sebesar 50 meter guna mengantisipasi galat pergeseran GPS satelit hulu.

### 3. `vault.py` — Enkripsi PII & Kepatuhan Ganda GDPR (Pasal 17)
*   **Anonimisasi Satu-Arah:** Mengaburkan data pribadi sensitif (Nama Petani dan Nomor Induk Berusaha / NIB) dari tabel transaksional utama `plots` dan log pabean `audit_ledger`, digantikan oleh token satu arah SHA-256:
    $$\text{association\_token} = \text{SHA-256}(\text{farmer\_name} \parallel \text{nib})$$
*   **AES-256 Cryptographic Vault:** Menyimpan asosiasi data identitas asli secara terisolasi di dalam tabel terenkripsi penuh `secure_personal_data_vault` menggunakan standar enkripsi simetris Fernet (AES-256).
*   **Mekanisme Key Shredding:** Jika petani menuntut hak penghapusan data sesuai GDPR Pasal 17, sistem menghancurkan kunci dekripsi data terkait. Rantai sejarah audit pengapalan tetap utuh dan valid secara matematis untuk kepatuhan EUDR, namun data identitas pribadi petani telah musnah secara kriptografis tanpa menyisakan jejak.

### 4. `zkv_engine.py` — Sirkuit Bukti Tanpa Pengungkapan (Groth16 Secp256r1)
*   **Trusted Setup & Proving:** Bertindak sebagai *Prover* domestik Indonesia yang memegang data HGU mentah yang dilindungi rahasia negara. Sirkuit Groth16 mengevaluasi kesesuaian spasial secara luring di server lokal, membangkitkan tanda tangan digital biner matematika $\pi(r, s)$ yang ringkas menggunakan kunci pembuktian privat (*Proving Key - PK*) berbasis kurva eliptik Secp256r1 (P-256).
*   **Asymmetric Verification:** Verifikator pabean Eropa di gerbang TRACES NT memegang kunci verifikasi publik (*Verifying Key - VK*) untuk mengeksekusi fungsi verifikasi asimetris:
    $$\text{verify\_zk\_proof}(\pi, x) \rightarrow \text{True} / \text{False}$$
    Pabean Eropa memverifikasi keabsahan kepatuhan lahan tanpa pernah melihat koordinat spasial HGU asli hulu.

### 5. `cryptography.py` — Segel Stempel Waktu Terpercaya eIDAS (RFC 3161)
*   **Integritas Anti-Tamper:** Menghitung sidik jari digital (SHA-256 Hash) dari seluruh berkas dokumen pengapalan JSON-LD.
*   **QTSP REST Handshake:** Mengirimkan payload permintaan biner ASN.1 DER-encoded secara asinkron ke server Qualified Trust Service Provider (QTSP) resmi Uni Eropa (seperti DigiCert/InfoCert).
*   **eIDAS Certified Timestamping:** Menerima dan menyegel berkas biner `.tsr` (Time-Stamp Response) terenkripsi resmi yang membuktikan secara hukum di pengadilan Uni Eropa bahwa data spasial dan transaksi tidak mengalami perubahan setelah tanggal penerbitan stempel waktu.

### 6. `flow_modeling.py` — Pemodelan Aliran Transien CSTR & Aktuasi PLC Industri
*   **Persamaan Neraca Massa Transien:** Memodelkan tangki penyimpanan CPO di pabrik pengolahan kelapa sawit sebagai reaktor pencampuran kontinu (CSTR). Sistem secara dinamis menghitung akumulasi konsentrasi kontaminasi minyak ilegal ($C$) menggunakan integrasi numerik Euler setiap menit:
    $$\frac{d(V(t) \cdot C(t))}{dt} = Q_{\text{in}}(t) \cdot C_{\text{in}}(t) - Q_{\text{out}}(t) \cdot C_{\text{out}}(t)$$
*   **Modbus TCP Actuation:** Jika konsentrasi kontaminasi fluida non-compliant terdeteksi melampaui ambang batas tanpa toleransi ($\le 0.001$), backend asinkron langsung menulis nilai bit **`1`** pada register perangkat kontrol perangkat keras PLC pabrik (*write-register*) melalui protokol Modbus TCP/OPC-UA. PLC secara fisik menggerakkan katup bypass pneumatik untuk membelokkan minyak tercemar ke tangki isolasi khusus domestik secara otomatis.

### 7. `fallback_manager.py` — Protokol Darurat & Mitigasi Risiko Stokastik
*   **Otomasi Peramban Playwright:** Jika pengiriman M2M mengalami kegagalan berturut-turut sebanyak 3 kali akibat kegagalan jaringan pabean Eropa, sistem asinkron meluncurkan bot peramban *Playwright* tanpa kepala (headless) melewati proxy IP domestik Uni Eropa. Bot mensimulasikan login EORI, mengisi formulir DDS, mengunggah berkas spasial secara fisik, menyegel tangkapan layar bukti audit di folder `/app/screenshots/`, serta menarik nomor rujukan URN secara otomatis dari DOM halaman web.
*   **Dynamic Split Shipment:** Memecah satu manifes pengapalan raksasa secara dinamis menjadi beberapa sub-manifes kecil berkapasitas aman (maksimal $\le 1.000$ ton kargo dan $\le 50$ poligon lahan per dokumen DDS) untuk menghindari kegagalan ekspor total jika terjadi masalah data spasial pada salah satu poligon penyuplai:
    $$N = \max \left( \left\lceil \frac{\text{Total Volume Kargo}}{1.000\text{ MT}} \right\rceil, \left\lceil \frac{\text{Jumlah Total Poligon}}{50} \right\rceil \right)$$

---

## 🗄️ MODEL DATA & STRUKTUR TABEL database POSTGIS

Skema DDL didefinisikan secara transaksional di dalam `app/models.py` dan dideploy secara horizontal menggunakan kontrol migrasi **Alembic**:

```sql
-- 1. Tabel Referensi Spasial HGU Prioritas I (Kedaulatan Agraria)
CREATE TABLE hgu_prioritas_1 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nomor_sertifikat VARCHAR UNIQUE NOT NULL,
    pemegang_hak VARCHAR NOT NULL,
    luas_sertifikat_ha DOUBLE PRECISION NOT NULL,
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_hgu_prioritas_1_geom ON hgu_prioritas_1 USING GIST (geom);

-- 2. Tabel Referensi Kawasan Hutan Prioritas III (Saringan Konflik)
CREATE TABLE kawasan_hutan_prioritas_3 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nama_kawasan VARCHAR NOT NULL,
    fungsi_hutan VARCHAR NOT NULL,
    sk_menhut VARCHAR,
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_kawasan_hutan_prioritas_3_geom ON kawasan_hutan_prioritas_3 USING GIST (geom);

-- 3. Tabel Lahan dengan Kolom Indeks Uber H3 & Quota Ledger
CREATE TABLE plots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plot_id VARCHAR UNIQUE NOT NULL,
    farmer_name VARCHAR NOT NULL, -- Menyimpan Token Asosiasi GDPR jika di-vault
    nib VARCHAR NOT NULL,         -- Menyimpan Token Asosiasi GDPR jika di-vault
    commodity VARCHAR DEFAULT 'Oil Palm' NOT NULL,
    area_ha DOUBLE PRECISION NOT NULL,
    annual_quantity_estimate_mt DOUBLE PRECISION NOT NULL,
    sisa_kuota_berjalan DOUBLE PRECISION NOT NULL, -- ACID Quota Ledger
    geom GEOMETRY(Polygon, 4326) NOT NULL,
    h3_indices VARCHAR[],         -- Alamat Array Uber H3 Hexagonal (Resolusi 11)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_plots_geom ON plots USING GIST (geom);
CREATE INDEX idx_plots_h3_gin ON plots USING GIN (h3_indices); -- GIN Index untuk pencarian O(1)

-- 4. Tabel Master Audit Ledger Terpartisi SQL Declarative Range Partitioning
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

-- 5. Sub-Tabel Partisi Range Fisik database
CREATE TABLE audit_ledger_2026_q2 PARTITION OF audit_ledger
    FOR VALUES FROM ('2026-04-01 00:00:00+00') TO ('2026-07-01 00:00:00+00');
CREATE TABLE audit_ledger_2026_q3 PARTITION OF audit_ledger
    FOR VALUES FROM ('2026-07-01 00:00:00+00') TO ('2026-10-01 00:00:00+00');
CREATE TABLE audit_ledger_2026_q4 PARTITION OF audit_ledger
    FOR VALUES FROM ('2026-10-01 00:00:00+00') TO ('2026-12-31 23:59:59+00');
```

---
## ⚓ SPESIFIKASI ENDPOINT API (KONTRAK PAYLOAD)

### 1. Webhook Penerimaan Nota Timbang (WhatsApp Gateway)
Menerima data transaksi biner gambar nota dari koperasi tani di lapangan hulu.
*   **Endpoint:** `POST /api/v1/webhook/whatsapp`
*   **Content-Type:** `multipart/form-data`
*   **Parameter Form:**
    
    | Nama Parameter | Tipe Data | Status | Deskripsi / Validasi |
    | :--- | :--- | :--- | :--- |
    | `file` | `Binary (File)` | Wajib | Berkas nota timbang (`image/jpeg` atau `image/png`). Harus memiliki EXIF metadata koordinat. |
    | `plot_id` | `String` | Wajib | Identifier unik plot lahan petani hulu. |
    | `nib` | `String` | Wajib | 13-digit angka standar OSS Indonesia (Wajib lolos regex validasi). |
    | `farmer_name` | `String` | Wajib | Nama lengkap petani swadaya penyuplai. |
    | `claimed_lat` | `Float` | Wajib | Lintang lokasi klaim fisik lahan ($\ge -90$ dan $\le 90$). |
    | `claimed_lon` | `Float` | Wajib | Bujur lokasi klaim fisik lahan ($\ge -180$ dan $\le 180$). |
    | `area_ha` | `Float` | Wajib | Luas total area komoditas dalam satuan Hektar. |

*   **Respons Sukses (HTTP 200 OK):**
    ```json
    {
      "status": "ACCEPTED",
      "message": "Kargo dari petani Kelompok Tani Inhu Makmur didaftarkan ke antrean Kafka (Tahap 1: Vision/OCR)."
    }
    ```

### 2. Simulasi Aliran Data Komprehensif (Siklus Pengujian)
Pemicu internal untuk mengeksekusi pengujian fungsional seluruh pipa data hulu-hilir secara deterministik.
*   **Endpoint:** `POST /api/v1/test/simulate-full-pipeline`
*   **Respons Sukses (HTTP 200 OK):**
    ```json
    {
      "simulation_status": "SUCCESS_FULL_CYCLE_COMPLIANT",
      "pabean_gateways": {
        "g2g_national_token": "TOKEN_G2G_ID_XXXX_2026",
        "traces_nt_response": {
          "status_code": 201,
          "urn_reference": "URN-DDS-XXXX",
          "submission_status": "ACCEPTED",
          "timestamp": "2026-06-22T19:48:00Z",
          "environment": "PRODUCTION_ZKV_GATEWAY",
          "validation_metadata": {
            "g2g_token_applied": "TOKEN_G2G_ID_XXXX_2026",
            "zk_circuit_status": "VERIFIED_COMPLIANT_NO_RAW_GEOMETRY_EXPOSED"
          }
        }
      },
      "yield_verification_engine_acid": {
        "measured_area_ha": 5.5,
        "annual_biological_ceiling_mt": 116.87,
        "remaining_quota_after_debit_mt": 104.37
      },
      "audit_readiness_reports": {
        "pilar_1_lineage_backtrack": { ... },
        "pilar_2_classification_accuracy": { ... },
        "pilar_3_database_anti_tamper": { ... }
      },
      "sealed_evidentiary_cluster": { ... }
    }
    ```

---

## 🛠️ PANDUAN DEPLOYMENT LOKAL (DOCKER ENVIRONMENT)

Layanan ini dikemas secara utuh di dalam kontainer Docker terkoordinasi melalui berkas `docker-compose.yml` di dalam direktori root.

### 1. Inisialisasi Environment (.env)
Salin file konfigurasi lingkungan dan sesuaikan variabel kunci rahasia Anda:
```bash
cp .env.example .env
```
*Pastikan parameter `DATABASE_URL` menggunakan nama host kontainer database internal Docker:*
```text
DATABASE_URL=postgresql+asyncpg://eudr_admin:secure_password_2026@db:5432/geoai_eudr_db
```

Seluruh variabel konfigurasi runtime harus didaftarkan di dalam berkas `.env` lokal untuk mengendalikan perilaku kontainer mikroservis:

```text
# ==========================================
# POSTGRES / POSTGIS DATABASE CONFIGURATION
# ==========================================
POSTGRES_USER=eudr_admin                 # Username database administratif
POSTGRES_PASSWORD=secure_password_2026   # Password database (Wajib diganti di produksi)
POSTGRES_DB=geoai_eudr_db                # Nama database utama
POSTGRES_HOST=db                         # Host kontainer (Mengarah ke layanan 'db' di docker-compose)
POSTGRES_PORT=5432                       # Port internal database
DATABASE_URL=postgresql+asyncpg://...    # URL asinkron utama untuk SQLAlchemy/asyncpg

# ==========================================
# COGNITIVE AI & OCR INTERFACES
# ==========================================
GEMINI_API_KEY=AIzaSy...                 # Kunci API untuk parser semantik model Gemini-1.5
OPENAI_API_KEY=sk-proj-...               # Kunci API cadangan untuk LLM GPT-3.5

# ==========================================
# TRACES NT & CUSTOMS CREDENTIALS
# ==========================================
TRACES_CLIENT_ID=ID-EORI-2026-...       # EORI/Client ID terdaftar di pabean Eropa
TRACES_CLIENT_SECRET=SEC-MOCK-2026...   # Client Secret OAuth 2.0 untuk jabat tangan M2M
TRACES_ENVIRONMENT=PRODUCTION_ZKV_GATEWAY# Jalur tujuan transmisi (SANDBOX / PRODUCTION)

# ==========================================
# GRAPH DATABASE CONFIGURATION (NEO4J)
# ==========================================
GRAPH_USER=neo4j                         # Username administratif grafik Neo4j
GRAPH_PASSWORD=secure_graph_password_2026# Sandi pengaman database silsilah Neo4j
```

### 2. Putar Infrastruktur Terdistribusi (Docker Compose)
Bangun citra lokal FastAPI dan jalankan seluruh gugusan kontainer di latar belakang secara paralel:
```bash
docker-compose up --build -d
```
*Perintah ini akan menyalakan kontainer:*
*   `db` (PostgreSQL 15 + PostGIS 3.3) pada port `5434`
*   `redis` (Redis 7) pada port `6379`
*   `neo4j` (Graph database) pada port `7474` / `7687`
*   `kafka` (Kafka Broker + KRaft engine) pada port `9092`
*   `api` (FastAPI Server + Workers AIOKafka) pada port `8000`

### 3. Eksekusi Pembaruan Skema Spasial (Alembic)
Jalankan migrasi DDL dari dalam kontainer API untuk menginisialisasi tabel-tabel pabean dan partisi:
```bash
docker exec -it eudr_fastapi alembic upgrade head
```

### 4. Diagnostik Kesehatan Layanan (Health Check)
Pastikan status FastAPI server dan pipa Kafka Broker berjalan normal:
```bash
curl -X GET http://localhost:8000/health
```
*Respons Sukses:*
```json
{"status": "ok", "service": "GeoAI EUDR Pipeline with Lifespan & Kafka is running"}
```

---

## 🚦 PROTOKOL PENGUJIAN INTEGRASI (THE END-TO-END DEMO)

Untuk menguji seluruh sirkuit pipa data hulu-hilir (Satelit $\rightarrow$ PostGIS $\rightarrow$ Kafka $\rightarrow$ ZKV $\rightarrow$ eIDAS $\rightarrow$ TRACES NT) dalam satu siklus asinkron yang aman, kirim kueri simulasi berikut:

*   **Menggunakan Perintah HTTP POST (cURL):**
    ```bash
    curl -X POST http://localhost:8000/api/v1/test/simulate-full-pipeline
    ```
*   **Melalui Swagger UI Dokumentasi Interaktif:**
    Aksesi `http://localhost:8000/docs` di peramban Anda, cari rute hijau **`POST /api/v1/test/simulate-full-pipeline`**, klik *"Try it out"*, lalu tekan *"Execute"*.

Sistem akan melakukan seeding otomatis koordinat spasial, memotong kuota berjalan, melakukan audit spasial multilayer, mengonversinya menjadi payload JSON-LD TRACES NT, meminta stempel waktu QTSP Eropa, serta menyegel berkas pabean biner akhir secara otonom dalam hitungan milidetik.

---

## 📜 IMMUTABLE LOGGING & DIAGNOSTIK PRODUKSI

Sistem menggunakan pustaka `structlog` untuk mencetak log terstruktur dalam format JSON yang kaya metadata ke konsol kontainer, memudahkan agregasi log oleh sistem monitoring eksternal (seperti ELK Stack atau Grafana Loki):

```json
{"timestamp": "2026-06-22T19:48:00.125Z", "level": "info", "logger": "geoai_eudr", "event": "pii_vaulted_successfully", "association_token": "8b6530621357fff..."}
{"timestamp": "2026-06-22T19:48:01.320Z", "level": "info", "logger": "geoai_eudr", "event": "qtsp_timestamp_received_real", "token_id": "TS-TOKEN-INFOCERT-998811"}
{"timestamp": "2026-06-22T19:48:02.045Z", "level": "info", "logger": "geoai_eudr", "event": "worker_2_spatial_success", "plot_id": "PLOT-INHU-001", "status": "COMPLIANT_SAVED"}
```