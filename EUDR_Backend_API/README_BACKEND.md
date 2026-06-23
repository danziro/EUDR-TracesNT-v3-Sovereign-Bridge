# EUDR Backend API & Cryptographic Trust Ledger (The Bits Engine)

---

## 🏛️ BAB 1: EXECUTIVE OVERVIEW & SOVEREIGN BITS ENGINE CARD

Dalam arsitektur *Sovereign RegTech Protocol (SRP)*, **`EUDR_Backend_API`** bertindak sebagai **The Bits Engine**—sebuah mesin orkestrasi transaksi, isolasi data pribadi, dan kompilator pabean hilir yang mutlak. Layanan ini bertanggung jawab mengubah klaim fisik hulu yang dihasilkan oleh *The Atoms Engine* menjadi bukti administrasi digital yang sah secara hukum, transaksional, dan tidak terbantahkan (*non-repudiation*) di pelabuhan pabean Uni Eropa.

Per Juni 2026, sisa waktu penegakan hukum administratif untuk perusahaan skala *enterprise* di bawah amandemen **Regulation (EU) 2025/2650** menyusut hingga **6 bulan** (tenggat waktu kepatuhan: 30 Desember 2026). Layanan ini dirancang khusus untuk mengeliminasi ketergantungan pada otoritas terpusat asing, melestarikan kedaulatan data spasial agraria nasional hulu, sekaligus menjamin kelancaran likuiditas ekspor hilir di bawah yurisdiksi kepatuhan Uni Eropa.

### 🛡️ KARTU SPESIFIKASI TEKNIS LAYANAN (*LAYERS & STACK INTEGRITY*)

| Parameter Sistem | Komponen & Teknologi Utama | Operasi Teknis yang Dieksekusi |
| :--- | :--- | :--- |
| **Core Web Server** | FastAPI (Python $\ge$ 3.10) | RESTful API non-blocking dengan asinkron Lifespan & Dependency Injection. |
| **Message Broker** | Confluent Kafka / KRaft | *Decoupling* asinkron untuk menjamin *throughput* tinggi pada proses ingesti massal. |
| **Spatial Database** | PostgreSQL 15 + PostGIS 3.3 | Penyimpanan poligon spasial, kueri interseksi spasial, dan *Declarative Range Partitioning*. |
| **In-Memory Cache** | Redis 7 (Alpine) | Manajemen sesi *caching*, pembatasan laju request (*rate-limiting*), dan mitigasi redundansi I/O. |
| **Graph Database** | Neo4j 5.18 | Pemodelan silsilah logistik rekursif hulu-hilir untuk mendeteksi fraksionasi kargo (*split shipment*). |
| **PII Cryptography** | Fernet AES-256 Symmetric | Isolasi dan enkripsi data pribadi petani swadaya untuk kepatuhan mutlak GDPR Pasal 17. |
| **Sovereign Proof** | ZK-SNARKs Groth16 | Verifikasi kedaulatan asimetris kurva Secp256r1 tanpa mengekspos batas fisik HGU asli hulu. |
| **Customs Sealer** | eIDAS Qualified Timestamp | Konstruksi kueri biner ASN.1 DER (RFC 3161) menuju QTSP Eropa untuk penerbitan token `.tsr`. |

---

## 🔄 BAB 2: DIAGRAM ALIR ARSITEKTUR MIKROSERVIS (EVENT-DRIVEN TOPOLOGY)

Layanan ini dirancang menggunakan arsitektur *event-driven* terdekopel (*asynchronous decoupling*) menggunakan Apache Kafka untuk memisahkan beban kerja komputasi intensif (proses visual OpenCV, EasyOCR, dan parsing LLM) dari operasi tulis transaksional basis data spasial (PostGIS, Quota Ledger, dan GDPR Vaulting).

### 1. Diagram Aliran Data Siber-Fisik (*End-to-End Ingestion Flow*)

```text
       [ WhatsApp Client / Webhook ]
                     │ (Biner Foto & JSON Metadata)
                     ▼
         [ FastAPI HTTP Web Server ] (app/main.py)
                     │
                     │ (Respons HTTP 202 - Accepted <50ms)
                     ├──────────────────────────────────────────────────────┐
                     ▼                                                      ▼
        [ Kafka Producer: Publish ]                                  [ WhatsApp Client ]
       (Topic: event.raw_ingestion)                           "Kargo Diterima, Proses Antrean..."
                     │
                     ▼
        [ Apache Kafka Broker Pool ]
                     │
     ┌───────────────┴───────────────┐
     ▼ (Consume)                     ▼ (Consume)
[ WORKER 1: VISION/OCR LOOP ]   [ WORKER 2: SPATIAL/ACID LOOP ]
(Topic: event.raw_ingestion)    (Topic: event.geo_validation)
     │                               │
     ├─► Ekstraksi EXIF GPS          ├─► Sanitasi Poligon Shapely 2D
     ├─► OpenCV Thresholding         ├─► Indeks Hexagonal Uber H3 (R11)
     ├─► EasyOCR Text Extraction     ├─► PostGIS Multilayer Intersection
     └─► Gemini/GPT LLM Parser       ├─► YVE & ACID Quota Ledger Deduct
             │                       ├─► PII Vaulting (Fernet AES-256)
             │                       └─► Immutable Ledger Partitioning
             ▼                               │
    [ Publish ke Broker ]                    ▼
(Topic: event.geo_validation)    (Jika sukses: Terbitkan URN DDS & TSR)
             │
             ▼ (Jika Gagal / Deviasi Jarak >100m)
   [ DEAD-LETTER QUEUE (DLQ) ]
       (Topic: event.dlq)
```

### 2. Mekanisme Kerja Dual-Worker Pipeline

Pemisahan tanggung jawab komputasi diatur secara ketat melalui dua utas pekerja latar belakang (*background worker threads*) yang berjalan secara non-blocking di dalam modul `app/services/kafka_manager.py`:

#### UTAS 1: `worker_vision_ocr()` — Pemrosesan Piksel & Ekstraksi Semantik
1.  **Penerimaan Event:** Mengonsumsi pesan mentah berisi biner gambar berformat Base64 dari topik `event.raw_ingestion`.
2.  **Verifikasi Forensik EXIF:** Membaca metadata gambar menggunakan `PIL.ExifTags`. Menguji koordinat fisik pengambilan foto terhadap koordinat klaim geofence hulu menggunakan rumus Haversine. Jika jarak deviasi $> 100$ meter, transaksi dianggap tidak sah dan dilempar ke topik `event.dlq` untuk isolasi.
3.  **Computer Vision & Adaptive Thresholding:** Mengonversi citra menjadi skala keabu-abuan (*grayscale*) dan menjalankan filter adaptif Gaussian (`cv2.adaptiveThreshold`) untuk menghilangkan bayangan kertas dan mengoptimalkan kontras karakter teks pada nota timbang hulu.
4.  **EasyOCR & Parsing Semantik LLM:** Pustaka `easyocr` dijalankan menggunakan mekanisme *Lazy Loading* untuk menghemat alokasi RAM kontainer. Hasil ekstraksi teks mentah dikirim ke mesin generator `Gemini-1.5-Flash` atau `GPT-3.5-Turbo` menggunakan kontrak prompt audit kaku untuk menghasilkan struktur JSON murni berisi `extracted_farmer_name` dan `extracted_quantity_mt`.
5.  **Pelepasan Event:** Hasil parsing yang valid dikemas ulang dan dirilis ke topik `event.geo_validation`.

#### UTAS 2: `worker_spatial_ledger()` — Verifikasi Spasial & Komitmen Transaksi ACID
1.  **Penerimaan Event:** Mengonsumsi data terstruktur hasil ekstraksi OCR dari topik `event.geo_validation`.
2.  **Sanitasi Geometri 2D & H3 Indexing:** Menjalankan pembersihan topologi poligon batas lahan menggunakan Shapely (Douglas-Peucker toleransi 1.5m dan pembersihan cincin berpotongan via `buffer(0)`). Poligon yang telah steril diubah menjadi sekumpulan alamat koordinat hexagonal **Uber H3 Resolusi 11** untuk mempercepat kueri spasial.
3.  **Kueri Multilapis PostGIS & Auto-Clipping:** Menguji irisan spasial poligon terhadap tabel referensi hukum nasional `hgu_prioritas_1` dan `kawasan_hutan_prioritas_3`. Jika terdeteksi tumpang tindih kawasan hutan tanpa dasar sertifikat HGU yang sah, sistem mengeksekusi pemotongan otomatis (*ST_Difference*) dengan toleransi *buffer* pengaman sebesar 50 meter.
4.  **GDPR Vaulting (Isolasi PII):** Memotong keterkaitan data pribadi hulu secara fisik. Nama petani dan NIB asli dikirim ke modul `vault.py` untuk dienkripsi menggunakan Fernet AES-256 dan disimpan di dalam database terisolasi `secure_personal_data_vault`. Hanya string hash searah `association_token` yang disimpan di dalam tabel publik `plots`.
5.  **ACID Quota Ledger:** Membuka transaksi basis data terisolasi menggunakan driver asinkron `asyncpg`. Sistem mengevaluasi kapasitas panen biologis maksimum tahunan (*Yield Verification Engine - YVE*) pada plot terkait. Jika saldo kuota berjalan `sisa_kuota_berjalan` memenuhi, sistem melakukan pengurangan kuota murni secara ACID. Jika saldo habis, transaksi ditolak oleh database untuk memblokir penipuan pemakaian koordinat berulang (*double-spending prevention*).
6.  **Pencatatan Audit Ledger:** Menuliskan mutasi transaksi secara *append-only* ke dalam tabel terpartisi `audit_ledger`. Sesi database dikomit secara asinkron.

---

## 🌐 BAB 3: MATRIKS BEDAH TEKNIS MODUL LAYANAN (THE CORE SERVICES)

Seluruh logika operasi silsilah kepatuhan diatur secara granular di bawah direktori `app/services/`. Setiap modul dirancang untuk menyelesaikan satu fungsi kepatuhan hukum atau ketahanan operasional secara asinkron dan terisolasi.

### 3.1. Ingestion & Forensik EXIF (`app/services/ingestion.py`)

Modul ini bertanggung jawab atas gerbang masuk pertama data fisik dari lapangan hulu, melakukan ekstraksi metadata biner, penapisan anomali jarak, dan pengubahan teks citra menjadi data terstruktur.

*   **Ekstraksi Metadata EXIF:** Menggunakan penafsiran langsung terhadap byte biner gambar untuk memisahkan tag GPS metadata (`GPSLatitude`, `GPSLongitude`, dan `DateTimeOriginal`).
*   **Validasi Deviasi Spasial (Haversine Filter):** Sistem menguji jarak linier antara koordinat geografis absolut hasil perekaman foto dengan koordinat geofence lahan hulu yang diklaim petani menggunakan rumus Haversine:
    $$d = 2R \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)$$
    *   *Liabilitas Bisnis:* Jika jarak deviasi $d > 100$ meter, sistem mendeteksi manipulasi lokasi (*spoofing*). Transaksi otomatis ditolak dan diarahkan ke antrean Dead-Letter Queue (DLQ) untuk mencegah masuknya buah ilegal dari luar geofence legal.
*   **Adaptive Thresholding & LLM Parser:** Citra nota timbang diproses melalui filter `cv2.adaptiveThreshold` dengan metode Gaussian untuk menghilangkan gangguan pencahayaan eksternal sebelum diekstrak oleh EasyOCR. Hasil teks mentah diumpankan ke model generator (`Gemini-1.5-Flash` atau `GPT-3.5-Turbo`) menggunakan skema output JSON kaku untuk menghasilkan data tonase murni (`extracted_quantity_mt`).

---

### 3.2. Sanitasi & Audit Spasial PostGIS (`app/services/geo_audit.py`)

Modul komputasi spasial relasional yang melakukan pembersihan topologi poligon dan pengujian tumpang tindih terhadap kawasan lindung nasional.

*   **Sanitasi Geometri 2D & Penyederhanaan:** Menggunakan pustaka Shapely untuk memaksa dimensi koordinat menjadi murni 2D via `force_geometry_2d` guna menghindari penolakan instan oleh skema API TRACES NT. Sistem menyederhanakan koordinat menggunakan algoritma Douglas-Peucker dengan toleransi spasial 1.5 meter (setara efisiensi simpul pabean) dan memperbaiki irisan diri sendiri (*self-intersection*) via operasi `buffer(0)`.
*   **Kueri Multilapis Spasial PostGIS:** Mengintegrasikan kueri SQL spasial asinkron untuk mendeteksi tumpang tindih lahan terhadap tabel referensi hukum nasional hulu secara riil:
    ```sql
    SELECT ST_Area(ST_Intersection(plot_geom, ST_Union(hgu.geom))) AS area_covered_hgu,
           ST_Area(ST_Intersection(plot_geom, ST_Union(hutan.geom))) AS area_conflict_forest,
           ST_AsText(ST_Difference(plot_geom, ST_Buffer(ST_Difference(hutan_union, hgu_union), 0.00045))) AS clean_geometry_wkt
    ```
*   **Auto-Clipping Logic:** Jika lahan terdeteksi masuk ke kawasan hutan lindung tanpa dilindungi sertifikat HGU yang sah (Prioritas I), sistem memotong area konflik tersebut dengan menambahkan toleransi *buffer* pengaman sebesar 50 meter (0.00045 derajat desimal) untuk menihilkan galat pergeseran GPS. Jika luas lahan bersih yang tersisa masih memenuhi batas minimum FAO ($\ge 0.5$ Hektar), pendaftaran diloloskan secara parsial; jika di bawah $0.5$ Ha, pengapalan ditolak otomatis.

---

### 3.3. GDPR Data Vault & Key Shredding (`app/services/vault.py`)

Modul ini menyelesaikan kontradiksi hukum internasional antara kewajiban audit 5 tahun (EUDR Pasal 11) dengan hak penghapusan data pribadi tanpa jejak (GDPR Pasal 17).

*   **Pemisahan Data & Pseudonimisasi:** Data pribadi yang sensitif (Nama Petani, Nomor NIB) disaring dari tabel spasial utama dan digantikan oleh hash satu arah SHA-256 (`association_token`):
    $$\text{association\_token} = \text{SHA-256}(\text{farmer\_name} \parallel \text{nib})$$
*   **Enkripsi Simetris AES-256 (Fernet):** Hubungan antara token dengan identitas asli disimpan di dalam basis data terisolasi `secure_personal_data_vault` dalam kondisi terenkripsi penuh menggunakan algoritma kunci simetris Fernet (AES-256) dengan rotasi kunci dinamis.
*   **Mekanisme Key Shredding:** Jika petani atau otoritas terkait menuntut penghapusan data pribadi mereka, admin mengeksekusi penghapusan baris kunci enkripsi terkait di dalam vault. Silsilah sejarah transaksi ekspor di dalam ledger utama tetap utuh dan valid (memenuhi EUDR), tetapi identitas fisik penyuplai hulu telah hancur secara kriptografis tanpa bisa didekripsi kembali oleh pihak mana pun (memenuhi GDPR).

---

### 3.4. Sovereign ZK-Bridge Prover-Verifier (`app/services/zkv_engine.py`)

Modul jembatan kedaulatan data nasional yang memvalidasi keabsahan wilayah hukum tanpa memaparkan koordinat fisik rahasia negara ke server pabean Uni Eropa.

*   **Prover Domestik (Sisi Indonesia):** Bertindak sebagai pembuat bukti tertutup menggunakan kunci pembuktian privat (*Proving Key - PK*) berbasis kurva eliptik Secp256r1 (P-256). Sistem memproses koordinat batas lahan riil, sertifikat HGU, dan peta hutan sebagai *Private Input (Witness - w)* di dalam server lokal dalam negeri. Hasil evaluasi melahirkan bukti tanda tangan matematika $\pi(r, s)$ yang ringkas.
*   **Verifier Internasional (Sisi Uni Eropa):** Server TRACES NT pabean Eropa hanya memegang kunci verifikasi publik (*Verifying Key - VK*) dan *Public Input (x)* berupa nilai hash dari berkas saksi (`witness_hash`) dan stempel waktu transaksi. Sistem mengeksekusi:
    $$\text{verify\_zk\_proof}(\pi, x) \rightarrow \text{True} / \text{False}$$
    Eropa mendapatkan kepastian matematis mutlak bahwa komoditas diproduksi di atas lahan legal yang bebas deforestasi, tanpa pernah memiliki kemampuan teknis untuk melihat atau merekonstruksi koordinat spasial HGU asli hulu.

---

### 3.5. eIDAS Qualified Electronic Sealer (`app/services/cryptography.py`)

Modul penyegelan bukti digital untuk menjamin prinsip *non-repudiation* yang diakui secara sah oleh institusi peradilan Uni Eropa berdasarkan regulasi eIDAS (EU No 910/2014).

*   **Penyusunan Kueri Biner ASN.1 DER:** Menghitung sidik jari digital (SHA-256 Hash) dari dokumen pabean JSON-LD. Mengonversi hash tersebut menjadi struktur biner ASN.1 DER `TimeStampReq` sesuai spesifikasi RFC 3161 untuk menghindari penolakan format oleh server sertifikasi Eropa.
*   **Qualified Timestamping (TSR):** Mengirimkan kueri biner tersebut ke server Qualified Trust Service Provider (QTSP) Eropa (seperti DigiCert/InfoCert) secara asinkron dengan batas timeout ketat 10 detik. Sistem menerima dan menyegel token biner `.tsr` (Time-Stamp Response) resmi yang tersinkronisasi langsung dengan jam atom global, mengunci keabsahan tanggal uji tuntas secara mutlak dari manipulasi tanggal mundur (*backdating*).

---

### 3.6. Aliran Kontinu & Aktuasi PLC Industri (`app/services/flow_modeling.py`)

Modul siber-fisik (*cyber-physical loop*) yang mengawasi kepatuhan silsilah logistik pada pengolahan minyak kelapa sawit mentah (CPO) di dalam silinder penyimpanan aktif hulu secara *real-time*.

*   **Integrasi Numerik Euler:** Silo penimbunan dimodelkan secara dinamis sebagai reaktor pengadukan kontinu (CSTR). Sistem menghitung pembaruan konsentrasi kontaminasi minyak ilegal ($C$) setiap menit menggunakan metode integrasi numerik Euler berdasarkan laju alir masuk ($Q_{\text{in}}$) dan keluar ($Q_{\text{out}}$):
    $$C(t + dt) = C(t) + \left( \frac{Q_{\text{in}}(t) \cdot C_{\text{in}}(t) - Q_{\text{out}}(t) \cdot C(t)}{V(t)} \right) \cdot dt$$
*   **Aktuasi PLC Industri (Modbus TCP):** Jika konsentrasi $C$ terdeteksi melampaui ambang batas tanpa toleransi ($\le 0.001$), backend asinkron langsung menulis nilai bit **`1`** pada register perangkat kontrol hardware PLC industri (*write-register*) menggunakan protokol Modbus TCP/OPC-UA. Sinyal ini secara fisik menggerakkan katup bypass pneumatik untuk membelokkan minyak tercemar keluar dari jalur ekspor utama menuju tangki isolasi domestik secara otomatis tanpa menghentikan jalur produksi.

---

### 3.7. Pengendali Darurat & Dynamic Split Shipment (`app/services/fallback_manager.py`)

Modul resiliensi operasional yang mengamankan kelancaran pengapalan fisik saat infrastruktur jaringan pabean Eropa mengalami kelumpuhan total (*packet loss/downtime*).

*   **Otomasi Peramban Playwright (RPA Fallback):** Jika pengiriman M2M API utama mengalami kegagalan berturut-turut sebanyak 3 kali, sistem menerapkan *Exponential Backoff*. Jika batas toleransi habis, sistem otomatis meluncurkan bot peramban *Playwright* tanpa kepala (headless) melewati proxy IP domestik Uni Eropa. Bot mensimulasikan otentikasi EORI, mengisi formulir DDS, mengunggah GeoJSON spasial, mengambil tangkapan layar bukti audit di folder `/app/screenshots/`, serta mengekstrak nomor rujukan URN secara otonom dari DOM halaman web konfirmasi pendaftaran.
*   **Dynamic Split Shipment:** Memotong risiko penolakan pengapalan total akibat adanya satu poligon penyuplai bermasalah di pelabuhan ekspor. Algoritma secara dinamis memecah satu manifes pengapalan raksasa menjadi sub-manifes kecil berkapasitas aman (maksimal $\le 1.000$ ton kargo dan $\le 50$ poligon lahan per dokumen DDS):
    $$N = \max \left( \left\lceil \frac{\text{Total Volume Kargo}}{1.000\text{ MT}} \right\rceil, \left\lceil \frac{\text{Jumlah Total Poligon}}{50} \right\rceil \right)$$
    Sub-manifes yang bersih diloloskan untuk dikapalkan, sementara sub-manifes yang bermasalah diisolasi untuk audit ulang tanpa menghentikan seluruh pengiriman kargo kapal.
	
---

## 🏗️ BAB 4: ARSITEKTUR BASIS DATA SPASIAL & SKEMA PARTISI RANGE

Pangkalan data PostgreSQL yang dikonfigurasi dengan ekstensi spasial **PostGIS** bertindak sebagai fondasi penyimpanan relasional berkinerja tinggi untuk melacak, memverifikasi, dan mencatat klaim batas lahan hulu secara instan.

### 4.1. Optimalisasi Indeks Hexagonal Uber H3 (GIN-Indexed Grid)

Operasi pengecekan tumpang tindih spasial (*spatial intersection*) tradisional di dalam database relasional menggunakan geometri poligon murni memiliki kompleksitas komputasi $O(N \cdot M)$ yang sangat berat, terutama ketika menangani jutaan plot lahan petani swadaya secara bersamaan. 

Untuk menghindari hambatan performa tersebut, `EUDR_Backend_API` mengimplementasikan sistem **GIN-Indexed Uber H3 Spatial Grid**:

1.  **Polyfill Geometri:** Setiap poligon batas lahan yang telah didekontaminasi oleh Shapely diubah menjadi sekumpulan alamat string hexagonal **Uber H3 Resolusi 11** (setara dengan luas cakupan tanah $\sim 2.000$ meter persegi atau 0.2 Hektar per hexagon).
2.  **Penyimpanan Kolom Array:** Alamat indeks hexagonal tersebut disimpan sebagai array string di dalam kolom `h3_indices` pada tabel `plots`.
3.  **Generalized Inverted Index (GIN):** Kolom array `h3_indices` didukung penuh oleh indeks GIN di tingkat basis data untuk mempercepat pencarian data bersarang.
4.  **Kueri Irisan Asinkron:** Kueri spasial tradisional digantikan oleh pencocokan operator irisan array `&&` yang sangat cepat:
    ```sql
    SELECT * FROM plots WHERE h3_indices && ARRAY['8b6530621357fff', '8b6530621350fff'];
    ```
    Metode ini memangkas kompleksitas pencarian tumpang tindih spasial dari $O(N \cdot M)$ menjadi secepat $O(1)$ di tingkat basis data, menjamin skalabilitas pencarian secara instan meskipun beban transaksi sedang tinggi.

### 4.2. Desain Declarative Range Partitioning (5-Year Audit Trail)

EUDR Pasal 11 mewajibkan penyimpanan data silsilah ekspor selama minimal 5 tahun untuk kebutuhan audit mendadak oleh Otoritas Kompeten Eropa. Menyimpan jutaan baris data log audit transaksional ke dalam satu tabel fisik tunggal dalam kurun waktu 5 tahun akan melambatkan kueri pencarian secara drastis (*indexing table bloat*).

Untuk mengatasinya, tabel `audit_ledger` dirancang menggunakan metode **PostgreSQL Declarative Range Partitioning** yang membagi data secara horizontal berdasarkan rentang waktu pembuatan (*Created At*):

*   **Aturan Kunci Utama Komposit:** Pada database terpartisi PostgreSQL, kolom penanda partisi waktu (`created_at`) wajib dikonfigurasi sebagai bagian dari *Composite Primary Key*:
    ```sql
    PRIMARY KEY (id, created_at)
    ```
*   **Pembagian Fisik Tabel Kuartalan:** Tabel dipecah secara horizontal ke dalam sub-tabel fisik independen berdasarkan kuartal tahun berjalan (Q2, Q3, Q4 2026):
    ```sql
    CREATE TABLE audit_ledger_2026_q2 PARTITION OF audit_ledger FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');
    CREATE TABLE audit_ledger_2026_q3 PARTITION OF audit_ledger FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');
    CREATE TABLE audit_ledger_2026_q4 PARTITION OF audit_ledger FOR VALUES FROM ('2026-10-01') TO ('2026-12-31 23:59:59');
    ```
*   **Mekanisme Partition Pruning:** Saat auditor melakukan penelusuran lineage mundur (*backtrack*) menggunakan filter tanggal tertentu, perencana kueri PostgreSQL secara dinamis melakukan *partition pruning* (hanya membuka dan mencari data pada sub-tabel kuartal fisik terkait) tanpa perlu merayapi (*scanning*) seluruh tabel sejarah audit 5 tahun.

---

## 🛠️ BAB 5: PANDUAN INSTALASI LOKAL & INFRASTRUKTUR KONTAINER

Seluruh komponen backend dan pangkalan data diisolasi menggunakan kontainer Docker yang dikoordinasikan secara terpusat melalui berkas `docker-compose.yml`.

### 5.1. Peta Kontainerisasi Mikroservis (`docker-compose.yml`)

Ketika Anda menjalankan Docker Compose, lima kontainer utama akan diputar secara paralel di latar belakang:

1.  **`db` (PostgreSQL 15 + PostGIS 3.3):** Menggunakan basis data spasial berkinerja tinggi yang mendengarkan pada port internal `5432` (diekspos ke port lokal `5434` untuk menghindari tabrakan dengan PostgreSQL lokal). Menjalankan skrip inisialisasi awal `docker/init-db.sql` untuk mengaktifkan ekstensi geospasial PostGIS dan pembuat UUID.
2.  **`redis` (Redis 7-Alpine):** Menyediakan penyimpanan memori sementara (*in-memory*) berkecepatan tinggi pada port `6379` untuk menangani pembatasan laju request (*rate-limiting*) dan manajemen sesi *caching* asinkron.
3.  **`neo4j` (Neo4j 5.18.0):** Menyediakan pangkalan data grafis pada port `7474` (HTTP) dan `7687` (Bolt) untuk melacak hubungan rekursif silsilah logistik hilir secara cepat.
4.  **`kafka` (Confluent Platform CP-Kafka 7.6.0):** Berjalan secara mandiri menggunakan protokol koordinasi KRaft (tanpa Zookeeper) pada port `9092` untuk mengelola antrean pesan asinkron.
5.  **`api` (FastAPI Application Server):** Membangun citra lokal menggunakan `docker/Dockerfile`, mengekspos port `8000` ke port lokal `8000`, menyinkronkan kode direktori hulu secara dinamis via *volumes*, serta menyalakan utas pekerja (worker) AIOKafka secara paralel saat kontainer dijalankan.

### 5.2. Penjelasan Konfigurasi Variabel Lingkungan (`.env.example`)

Salin berkas templat lingkungan publik menjadi berkas konfigurasi lokal:
```bash
cp .env.example .env
```

Berikut adalah penjelasan fungsi setiap kunci variabel lingkungan yang wajib dikonfigurasi sebelum menjalankan kontainer:

*   `DATABASE_URL`: URL koneksi asinkron utama ke pangkalan data PostGIS. *Wajib mengarah ke host 'db' (nama kontainer internal Docker) jika dijalankan di dalam Docker:*
    ```text
    DATABASE_URL=postgresql+asyncpg://eudr_admin:secure_password_2026@db:5432/geoai_eudr_db
    ```
*   `GEMINI_API_KEY` & `OPENAI_API_KEY`: Kunci otorisasi API untuk mengakses model bahasa besar (Gemini-1.5-Flash atau GPT-3.5) guna menangani parsing teks tidak terstruktur hasil pembacaan EasyOCR pada nota timbang hulu.
*   `TRACES_CLIENT_ID` & `TRACES_CLIENT_SECRET`: Kredensial OAuth 2.0 Client Credentials Flow untuk otorisasi mesin-ke-mesin (M2M) dengan server pabean Uni Eropa TRACES NT.
*   `GRAPH_USER` & `GRAPH_PASSWORD`: Kredensial otentikasi administratif untuk mengamankan koneksi asinkron ke database grafis silsilah Neo4j.

### 5.3. Prosedur Peluncuran & Migrasi database

Ikuti urutan eksekusi berikut untuk meluncurkan backend API dari awal secara bersih:

#### 1. Bangun Citra & Jalankan Kontainer (Docker Compose)
Unduh seluruh citra resmi dan jalankan kelima layanan di latar belakang secara paralel:
```bash
docker-compose up --build -d
```

#### 2. Eksekusi Migrasi database Spasial (Alembic)
Jalankan migrasi DDL dari dalam kontainer API yang sedang aktif untuk menginisialisasi tabel-tabel pabean, indeks spasial, dan partisi fisik:
```bash
docker exec -it eudr_fastapi alembic upgrade head
```

#### 3. Jalankan Pengujian Diagnostik Impor
Gunakan perintah diagnostik ini untuk memvalidasi bahwa seluruh modul Python, skema Pydantic, dan konektor database terintegrasi secara sempurna tanpa ada kesalahan penulisan kode atau kegagalan impor:
```bash
docker exec -it eudr_fastapi python -c "import app.main"
```

#### 4. Bersihkan Sisa Volume database (Hard Reset)
Jika Anda melakukan perubahan skema model atau ingin menguji instalasi dari kondisi kosong murni, bersihkan seluruh sisa kontainer beserta volume data persistennya menggunakan perintah:
```bash
docker-compose down -v
docker volume prune -f
```

---

## ⚙ ️BAB 6: SPESIFIKASI KONTRAK API & PROTOKOL PENGUJIAN SATU-KLIK

Layanan backend mengekspos gerbang masuk administratif dan simulasi terperinci untuk memfasilitasi pengujian alur data secara terintegrasi hulu-hilir.

### 6.1. Webhook Ingesti Nota Timbang (`POST /api/v1/webhook/whatsapp`)

Menerima berkas biner gambar nota timbang kelapa sawit mentah dan meluncurkannya ke dalam antrean Kafka.
*   **Content-Type:** `multipart/form-data`
*   **Parameter Validasi (Form Parameters):**

| Nama Parameter | Tipe Data | Aturan Validasi / Ekspresi Reguler | Deskripsi Sistem |
| :--- | :--- | :--- | :--- |
| `file` | `Binary (File)` | Wajib berupa berkas JPEG, JPG, atau PNG. | Berkas gambar nota timbang fisik hulu. |
| `plot_id` | `String` | Wajib diisi (tidak boleh kosong). | Identifier unik plot spasial lahan. |
| `nib` | `String` | Wajib berupa 13-digit angka (`^\d{13}$`). | Nomor Induk Berusaha hulu standar OSS Indonesia. |
| `farmer_name` | `String` | Wajib diisi. | Nama lengkap petani swadaya penyuplai komoditas. |
| `claimed_lat` | `Float` | Wajib berada pada rentang $\ge -90.0$ s/d $\le 90.0$ dan tidak boleh presisi nol. | Lintang lokasi klaim fisik lahan. |
| `claimed_lon` | `Float` | Wajib berada pada rentang $\ge -180.0$ s/d $\le 180.0$ dan tidak boleh presisi nol. | Bujur lokasi klaim fisik lahan. |
| `area_ha` | `Float` | Wajib bernilai positif $> 0.0$ Hektar. | Luas total area komoditas lahan penyuplai. |

*   **Respons Keberhasilan (HTTP 202 - Accepted):**
    ```json
    {
      "status": "ACCEPTED",
      "message": "Kargo dari petani Kelompok Tani Inhu Makmur didaftarkan ke antrean Kafka (Tahap 1: Vision/OCR)."
    }
    ```

---

### 6.2. Protokol Simulasi Pipa Penuh (`POST /api/v1/test/simulate-full-pipeline`)

Menjalankan simulasi deterministik (bebas acak) yang merangkum seluruh lima pilar asinkron SRP secara langsung dalam satu klik: seeding spasial hulu $\rightarrow$ sanitasi geometri 2D $\rightarrow$ pencocokan kuota $\rightarrow$ kompilasi JSON-LD TRACES NT $\rightarrow$ penyegelan stempel waktu eIDAS TSA $\rightarrow$ audit kesiapan URN.

*   **Respons Sukses (HTTP 200 - OK):**
    ```json
    {
      "simulation_status": "SUCCESS_FULL_CYCLE_COMPLIANT",
      "pabean_gateways": {
        "g2g_national_token": "TOKEN_G2G_ID_99AA88_2026",
        "traces_nt_response": {
          "status_code": 201,
          "urn_reference": "URN-DDS-99881122"
        }
      },
      "yield_verification_engine_acid": {
        "measured_area_ha": 5.5,
        "annual_biological_ceiling_mt": 116.88,
        "remaining_quota_after_debit_mt": 104.38
      },
      "audit_readiness_reports": {
        "pilar_1_lineage_backtrack": {
          "audit_pilar": "PILAR_I_DATA_LINEAGE",
          "urn_target_reference": "URN-DDS-99881122",
          "backtrack_execution_timestamp": "2026-06-23T23:48:00.125Z",
          "consignment_integrity_record": {
            "associated_plot_id": "PLOT-INHU-2026-MOCK-01",
            "deforestation_free_verdict": "COMPLIANT",
            "system_audit_timestamp": "2026-06-23T23:48:00Z",
            "blockchain_compliant_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
          },
          "raw_geospatial_evidence": {
            "registered_farmer_name": " Kelompok Tani Inhu Makmur",
            "tax_number_nib": "NIB-12340099",
            "measured_area_ha": 5.5,
            "raw_boundary_wkt": "POLYGON ((102.498 -0.381, 102.5 -0.381, 102.5 -0.383, 102.498 -0.383, 102.498 -0.381))"
          }
        },
        "pilar_2_classification_accuracy": {
          "audit_pilar": "PILAR_II_SPATIAL_ACCURACY",
          "evaluation_sampling_count_n": 1840,
          "calculated_overall_accuracy": 0.9728,
          "required_standard_threshold": 0.85,
          "audit_status": "PASSED"
        },
        "pilar_3_database_anti_tamper": {
          "audit_pilar": "PILAR_III_DATABASE_SECURITY",
          "total_plots_verified": 1,
          "tampered_plots_detected": 0,
          "database_status": "SECURE_INTEGRITY_VERIFIED"
        }
      }
    }
    ```

---

### 6.3. Logging Terstruktur Produksi (Production Structured Logs)

Sistem memuntahkan catatan log dalam bentuk string objek JSON terkompresi ke konsol kontainer API guna memfasilitasi integrasi otomatis dengan alat analisis log terpusat (seperti *Grafana Loki* atau *Elasticsearch*):

```json
{"timestamp": "2026-06-23T23:48:01.042Z", "level": "info", "logger": "geoai_eudr", "event": "pii_vaulted_successfully", "association_token": "8b6530621357fff..."}
{"timestamp": "2026-06-23T23:48:02.122Z", "level": "info", "logger": "geoai_eudr", "event": "qtsp_timestamp_received_real", "token_id": "TS-TOKEN-INFOCERT-998811"}
{"timestamp": "2026-06-23T23:48:03.002Z", "level": "info", "logger": "geoai_eudr", "event": "worker_2_spatial_success", "plot_id": "PLOT-INHU-2026-MOCK-01", "status": "COMPLIANT_SAVED"}
```

---

## 📜 BAB 7: BATAS LIABILITAS HUKUM & KONTRAK JASA (SLA INDEMNITY CAP)

Untuk mengamankan kepentingan komersial, operasional, dan finansial dari penyedia solusi teknologi *Sovereign RegTech Protocol (SRP)* terhadap risiko keuangan berat akibat yurisdiksi tanggung jawab mutlak (*Strict Liability*) pabean asing, kontrak kerja sama teknis diatur secara ketat oleh klausul perlindungan hukum berikut:

### 7.1. Status Hukum Sistem Pendukung Keputusan (*Decision-Support System*)

Sistem ini diklasifikasikan murni sebagai **Sistem Pendukung Keputusan (*Decision-Support System* - DSS)**. Hasil klasifikasi semantik kecerdasan buatan, visualisasi peta satelit hulu, pembatasan kuota panen, dan penentuan status kepatuhan ditujukan untuk membantu operator menyusun bukti pembelaan teknis kepabeanan (*customs technical dossier*). 

Layanan ini tidak bertindak sebagai jaminan kelolosan mutlak bebas galat, nasihat hukum formal, atau penjamin bebas sanksi pabean eksternal. Keputusan akhir atas kelolosan ekspor komoditas kelapa sawit sepenuhnya berada di bawah otoritas pabean Uni Eropa dan instansi bea cukai negara anggota terkait.

### 7.2. Batas Ganti Rugi Finansial Maksimal (*SLA Indemnity Cap*)

Nilai ganti rugi maksimal (*liability cap*) yang wajib dibayarkan oleh penyedia layanan jasa teknologi kepada klien atas setiap tuntutan hukum, klaim kerugian, investigasi pabean, atau kegagalan kepatuhan geospasial hulu dibatasi secara mutlak **maksimal setara dengan total biaya layanan (*service fee*) yang dibayarkan secara riil oleh klien dalam kurun waktu 12 bulan terakhir** sebelum terjadinya peristiwa tuntutan hukum terkait.

### 7.3. Pengecualian Kerugian Konsekuensial (*Exclusion of Consequential Damages*)

Penyedia jasa teknologi dibebaskan secara mutlak, penuh, dan tanpa pengecualian dari segala bentuk tuntutan ganti rugi atas:
*   Kerugian tidak langsung (*indirect damages*).
*   Kerugian konsekuensial (*consequential damages*) berupa kehilangan potensi pasar, hilangnya keuntungan bisnis (*lost profits*), penolakan pengapalan sepihak di pelabuhan tujuan, penyitaan kapal pengangkut komoditas fisik, atau denda administratif pabean Uni Eropa sebesar 4% omset tahunan importir berdasarkan Pasal 25 EUDR akibat adanya kesalahan penafsiran data spasial atau kegagalan integrasi M2M TRACES NT.