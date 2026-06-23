# 🛰️ Inhu GeoAI EUDR Compliance Engine (v4.0)
### *Advanced Remote Sensing, Spatio-Temporal Forensics & Legal Provenance Ingestion System*

---

## 🏛️ 1. DEKLARASI KEPATUHAN REGULASI & DISCLAIMER HUKUM

### A. Kerangka Regulasi Utama
Sistem ini dirancang khusus sebagai mesin kesiapan audit (*Audit Readiness*) untuk memenuhi kewajiban uji tuntas (*Due Diligence*) secara otomatis sesuai dengan regulasi Uni Eropa berikut:
1. **Regulation (EU) 2023/1115 (EU Deforestation Regulation - EUDR):** Khususnya Pasal 3 (Persyaratan Kumulatif Kepatuhan Bebas Deforestasi dan Legalitas), Pasal 9 (Persyaratan Informasi Geolokasi dan Poligon), serta Pasal 10 (Penilaian dan Mitigasi Risiko).
2. **Regulation (EU) 2025/2650 (Rezim Amandemen Penundaan & Penyederhanaan):** Mengintegrasikan persyaratan estimasi kuantitas tahunan produk serta mendukung mekanisme penyebaran *Union Reference Number* (URN) berjenjang (*Downstream Pass-Through*).
3. **eIDAS Regulation (EU) No 910/2014:** Memenuhi standar pembuktian hukum elektronik melalui penyegelan tanda tangan kriptografis dan stempel waktu terpercaya (*Qualified Electronic Time Stamps*) untuk menjamin prinsip non-penyangkalan (*non-repudiation*) bukti digital pabean.

### B. Status Hukum Sistem (Disclaimer)
*Sistem ini diklasifikasikan secara hukum sebagai **Sistem Pendukung Keputusan (Decision-Support System - DSS)**. Hasil analisis spasial, klasifikasi kelas kecerdasan buatan (AI), deteksi anomali temporal, dan verifikasi administratif dokumen lokal yang disajikan oleh sistem ini ditujukan untuk membantu operator dalam menyusun berkas pembelaan teknis (Customs Technical Dossier). Output dari sistem ini tidak menggantikan keputusan final Otoritas Kompeten Uni Eropa atau instansi kepabeanan negara anggota.*

---

## 🗺️ 2. ALUR KERJA ARSITEKTUR SISTEM (END-TO-END)

Sistem mengintegrasikan hulu data bumi (*Earth Observation*) dengan administrasi pabean hilir melalui delapan tahapan otomatisasi yang sinkron:

```
[Mulai Siklus Audit]
       │
       ▼
 [CODES 1] Ingesti Multi-Sensor (S1 RTC + S2 L2A) ──► Sentinel-2 Baseline (Q4 2020 Percentile 10)
       │                                              Sentinel-2 Ongoing (2026 Median Reducer)
       ▼
 [CODES 2] Delineasi Semantik (Prithvi-v2 Model) ──► Segmentasi AI & Poligonisasi Bidang Tanah
       │
       ▼
 [CODES 2] Sterilisasi Topologi & Koordinat ──────► Sanitasi 2D WGS84, Douglas-Peucker (Toleransi 1.5m),
       │                                              dan Aturan RFC 7946 Right-Hand Rule (CCW)
       ▼
 [CODES 2] Penyegelan Kripto & eIDAS ─────────────► Hash Chaining SHA-256 & Request Token TSR biner
       │                                              ASN.1 DER ke QTSP Server (DigiCert)
       ▼
 [CODES 3] Forensik Temporal & Iklim ─────────────► Koreksi El Niño (Pearsonr) & Deteksi Degradasi
       │                                              Sub-Piksel (Spectral Mixture Analysis - NPV)
       ▼
 [CODES 4] Verifikasi Dokumen Legal (Blok 0) ─────► Validasi Pydantic NIB, HGU, AMDAL, Pajak & ISPO
       │
       ▼
 [CODES 4] Generator DDS & Transmisi M2M ─────────► Perakitan JSON-LD, Transmisi API Gateway TRACES NT,
       │                                              dan Ekstraksi Union Reference Number (URN)
       ▼
 [CODES 4] Audit Trail Ledger & Pelaporan ────────► Append-Only JSONL Ledger & Ekspor HTML Report
```

---

## 🛠️ 3. FITUR UTAMA & RINCIAN TEKNIS PER MODUL (CODES 1 - 4)

### 🛰️ CODES 1: Advanced Data Ingestion & Cloud-Native Clearing
Modul ini bertugas membangun fondasi citra multispektral "Prithvi-Ready" yang bebas dari bias atmosferik tropis di wilayah Riau:
- **Fusi Sensor Multi-Modal:** Menggabungkan karakteristik penetrasi radar aktif Sentinel-1 (VV/VH cross-polarization) dengan visual multispektral Sentinel-2 L2A.
- **Kompensasi Awan Tropis (Baseline vs Ongoing):**
  - *Baseline (Q4 2020):* Menggunakan **Percentile 10 Lambda Reducer** untuk menyaring bayangan awan tebal (*cloud-shadow*) pada puncak musim hujan di akhir tahun 2020.
  - *Ongoing (2026):* Menggunakan **Median Reducer** untuk menangkap kestabilan tren kesehatan klorofil vegetasi saat musim panen berjalan.
- **Koreksi Medan Radiometrik (S1-RTC):** Memproses balik hamburan (*backscatter Intensity*) Sentinel-1 menggunakan model elevasi *Copernicus DEM 30m* untuk menihilkan gangguan distorsi topografi berlereng curam (*layover* dan *shadow*).
- **Optimasi COG (Cloud Optimized GeoTIFF):** Mentransformasikan hasil ingesti ke proyeksi metrik lokal **UTM Zona 47N (EPSG:32647)** dengan ukuran grid pixel 10x10 meter presisi tinggi, terkompresi LZW, serta dilengkapi struktur *internal overviews* internal.

### 📐 CODES 2: SAM 2 & Foundation Models for Precision Mapping
Modul pengolahan vektor dan pembuktian integritas data geografis sesuai dengan spesifikasi ketat sistem pabean Uni Eropa:
- **Delineasi Batas Lahan Semantik:** Memproses citra 6-band COG melalui model fondasi *Prithvi-v2* yang dilengkapi adapter LoRA khusus kelapa sawit (*Bio-Physical_Palm_Riau*) untuk memetakan probabilitas spasial murni vegetasi.
- **Sterilisasi Topologi RFC 7946:**
  - *Douglas-Peucker Simplification:* Menyederhanakan titik sudut (*vertices*) poligon menggunakan toleransi jarak 1.5 meter untuk memastikan efisiensi payload transmisi API.
  - *Strict 2D Enforcement:* Memotong dimensi Z (koordinat 3D) secara mutlak karena server pabean TRACES NT menolak elemen geometri 3D.
  - *Right-Hand Rule (CCW):* Mengatur arah putaran cincin koordinat luar poligon (*exterior ring*) wajib berputar berlawanan arah jarum jam (Counter-Clockwise).
- **Sliver & Noise Removal:** Menghapus poligon di bawah 0.1 Hektar (1000 $m^2$) untuk mengeliminasi noise hasil segmentasi tanpa mendistorsi plot utama.
- **Penyegelan Kriptografis eIDAS (ASN.1 DER request):** Mengubah nilai hash SHA-256 dari berkas GeoJSON steril menjadi kueri biner ASN.1 DER `TimeStampReq` (RFC 3161). Kueri dikirim ke server Qualified Trust Service Provider (QTSP) global untuk menerbitkan token bukti waktu `.tsr` biner yang sah secara hukum.
- **Penyegelan Kriptografis eIDAS (Linked Hash Chaining):**
  - Mengonversi berkas GeoJSON steril menjadi hash SHA-256.
  - Menyuntikkan hash tersebut bersama skor risiko dan segel legalitas hulu (*legal_seal* Blok 0) ke dalam struktur tanda tangan berantai (*Hash Chaining*).
  - Membawa payload hash tersebut dalam kueri biner ASN.1 DER `TimeStampReq` (RFC 3161) menuju QTSP server untuk mendapatkan token stempel waktu digital `.tsr` biner yang kebal manipulasi.

### 📈 CODES 3: Bio-Temporal & Change Detection Analysis
Modul forensik runtun waktu (*time-series*) yang bertugas menyajikan bukti ilmiah mutlak untuk membantah tuduhan deforestasi atau degradasi hutan:
- **Robust Multi-Format Parser:** Mengurai berkas luaran zonal statistics asinkron dari superkomputer CDSE openEO yang volatil. Parser secara adaptif mengenali skema data *standard results*, *FeatureCollection*, maupun *Flat Dict Timeseries*.
- **Pertahanan Iklim (El Niño Defense):** Melakukan analisis korelasi Pearson terlokalisasi (*Local Windowed Correlation*) pada jendela waktu kritis penurunan tajuk vegetasi terhadap indeks curah hujan CHIRPS/VPD. Korelasi lokal $> 0.75$ membuktikan secara ilmiah bahwa penurunan indeks kehijauan disebabkan oleh cekaman kekeringan ekstrem El Niño, bukan akibat aktivitas tebang liar.
- **Pertahanan Siklus Peremajaan (Replanting DTW):** Mengukur jarak kemiripan pola (*pattern similarity*) runtun waktu NDVI pasca-clearing menggunakan algoritma *Dynamic Time Warping* (DTW) terhadap kurva pertumbuhan kelapa sawit muda standar (Sigmoidal S-Curve). Jarak DTW $\le 0.18$ mengonfirmasi siklus peremajaan pertanian legal yang dilindungi Pasal 2(5) & 2(6) EUDR.
- **Dekomposisi Sub-Piksel SMA (Spectral Mixture Analysis):** Memecah spektral piksel murni campuran ke dalam fraksi *Non-Photosynthetic Vegetation* (NPV) untuk mendeteksi penumpukan kayu mati di lantai hutan akibat aktivitas *selective logging* terselubung.

### 🏛️ CODES 4: Production-Grade API, Risk Assessment & Reporting
Modul integrasi administratif, orkestrasi transaksional, dan visualisasi bukti audit:
- **Legal Document Verification Engine (Blok 0):** Memverifikasi integritas dokumen legalitas Indonesia:
  - Nomor Induk Berusaha (NIB 13-Digit).
  - Hak Guna Usaha (HGU) ATR/BPN.
  - Dokumen kelayakan lingkungan hulu (AMDAL/UKL-UPL/SPPL).
  - Persetujuan FPIC tertulis dengan masyarakat hukum adat.
  - Sertifikat kelayakan keberlanjutan sawit nasional **ISPO** (*Indonesian Sustainable Palm Oil*) beserta tahun penerbitannya.
- **Unified Orchestrator (Pydantic-Secured):** Menerapkan validasi data berlapis. Jika plot lahan $\ge 4.0$ Hektar, sistem mewajibkan pengisian berkas lintasan koordinat poligon GeoJSON tersterilisasi. Jika tidak dilampirkan, skema input otomatis memicu *Value Error* pabean.
- **TRACES NT JSON-LD DDS Generator:**
  - Merakit payload Due Diligence Statement (DDS) pabean berbasis metadata JSON-LD versi `2026.2`.
  - Mengunci kode pabean terharmonisasi 8-digit **CN-Code `15111090` (Crude Palm Oil)** secara otomatis.
  - Menyuntikkan koordinat poligon murni 2D ke dalam tag `geospatial_verification` untuk lahan $\ge 4.0$ Ha, serta menyematkan nomor registrasi sertifikasi kelayakan ISPO secara sah.
- **REST API M2M Connector:** Melakukan jabat tangan (*handshake*) autentikasi OAuth 2.0 Client Credentials Flow, pengiriman asinkron berkas DDS dengan sistem ketahanan *exponential backoff*, serta perekaman tanda terima (*receipt*) URN resmi dari Komisi Eropa di Google Drive.
- **Audit Trail Ledger & Reporting:** Mencatat setiap mutasi verifikasi spasial-legal dan transmisi pabean ke dalam berkas ledger lokal bertipe *append-only* JSONL. Membaca ledger tersebut untuk dikompilasikan menjadi halaman laporan kepatuhan final interaktif (HTML) yang diamankan oleh hash enkripsi.

---

## 💻 4. PRASYARAT SISTEM & PANDUAN INSTALASI

### A. Dependensi Perangkat Lunak (Python Stack)
Sistem ini membutuhkan Python versi $\ge 3.10$ dengan pustaka manipulasi data spasial, AI, dan kriptografi yang terdaftar di dalam `requirements.txt`. Pastikan dependensi berikut terinstal di lingkungan kerja (Google Colab / Local VM):

```bash
pip install openeo>=0.30.0 rasterio>=1.4.0 numpy>=2.1.0 matplotlib>=3.10.0 \
            folium>=0.17.0 pydantic>=2.12.0 pyproj>=3.7.0 geopandas>=1.0.0 \
            shapely>=2.0.0 scipy>=1.12.0 torch>=2.2.0 pandas>=2.2.0
```

### B. Struktur Direktori Google Drive (Google Drive Directory Tree)
Sistem menggunakan Google Drive sebagai media penyimpanan bukti digital (*evidence cache*) yang persisten. Direktori berikut akan dibuat secara otomatis pada eksekusi hulu:

```
/content/drive/MyDrive/GeoAI_EUDR_2026/
├── Cleaned_EUDR_Polygons_2026.geojson       # Vektor batas lahan steril 2D (CCW)
├── Prithvi_Baseline_2020.tif                 # Spektral Raster baseline (Q4 2020)
├── Prithvi_Ongoing_2026_COG.tif              # Spektral Raster metrik COG (2026)
├── Semantic_Prob_Map_2026.tif                # Peta Probabilitas Klasifikasi Kelas AI
├── Temporal_Profile_2020_2026.csv            # Database Runtun Waktu NDVI rill
├── EUDR_Audit_Evidence_2026_Pure.csv         # Laporan analisis bio-fisik murni
├── EUDR_Final_Submission_Data_2026.csv       # Kompilasi hasil audit forensik
├── EUDR_eIDAS_Timestamp.tsr                  # Bukti biner stempel waktu QTSP
└── Codes_4_Outputs/
    ├── Immutable_Audit_Ledger.jsonl          # Log audit append-only lokal
    │   DDS_Archive_2026/                     # Berkas payload DDS resmi (JSON-LD)
    │   EU_Official_Receipts/                 # Berkas URN tanda terima TRACES NT
    └── EUDR_Final_Report_2026.html           # Dasbor laporan audit final
```

### C. Autentikasi Copernicus CDSE & TRACES NT M2M
-   **CDSE OpenEO Connection:** Saat memanggil `connection.authenticate_oidc()`, pastikan Anda memiliki akun aktif di [Copernicus Dataspace Ecosystem](https://dataspace.copernicus.eu/). Di Google Colab, proses ini akan memicu pop-up otorisasi OAuth 2.0 yang meminta Anda masuk menggunakan kredensial CDSE.
-   **TRACES NT M2M Credentials:** Untuk pengiriman DDS, sistem memanfaatkan kunci `client_id` dan `client_secret`. Dalam pengujian Sandbox, kredensial ini menggunakan nilai tiruan otomatis. Di lingkungan produksi, Anda harus meregistrasikan EORI perusahaan di portal integrasi TRACES NT untuk memperoleh kunci OAuth 2.0 yang nyata.

---

## 🚀 5. PANDUAN MENJALANKAN SISTEM (EXECUTION GUIDE)

### A. Eksekusi Siklus Kepatuhan Penuh (Unified Production Compliance Cycle)
Siklus orkestrasi penuh dijalankan melalui fungsi eksekutor asinkron di **Codes 4 - Blok 5**. Jalankan seluruh blok dari awal hingga akhir di Google Colab, lalu panggil fungsi berikut:

```python
import asyncio

# Menjalankan siklus otomatisasi hulu-hilir
asyncio.run(run_production_compliance_cycle())
```

### B. Mekanisme Cache & Penghematan Kredit Komputasi (Resource Efficiency)
Untuk menghindari biaya pengunduhan data satelit berlebih dan mempercepat waktu eksekusi, sistem dilengkapi dengan **Smart Caching Layer**. 
*   Sebelum melakukan ingesti batch ke superkomputer Uni Eropa (CDSE), fungsi `get_eudr_evidence()` dan `run_production_batch_audit()` akan memeriksa keberadaan berkas `.tif` di Google Drive.
*   Jika berkas terdeteksi (Cache Hit), unduhan dilewati, menghemat waktu proses hingga beberapa menit dan menjaga kuota kredit CDSE Anda tetap utuh.

### C. Mekanisme Failsafe Fallback (Resiliensi Jaringan)
-   **Satelit & Iklim:** Jika server OpenEO CDSE Brussel mengalami gangguan jaringan (*downtime*) atau kegagalan autentikasi, sistem akan mengalihkan proses secara otomatis ke fungsi `generate_fallback_timeseries()`. Fungsi ini menyusun runtun waktu NDVI tiruan deterministik (bebas acak) yang secara matematis disesuaikan dengan profil historis Riau untuk menjaga kontinuitas uji coba.
-   **Kriptografi TSA:** Jika server QTSP DigiCert gagal merespons request biner RFC 3161 dalam batas waktu timeout 10 detik, `fetch_rfc3161_token` secara otomatis beralih ke *NTP synchronized Internal Time Authority* untuk menyegel sertifikat tanpa merusak urutan penulisan berkas.

---

## 🛡️ 6. NILAI PEMBUKTIAN HUKUM (LEGAL DEFENSIBILITY & AUDIT READINESS)

Sistem ini didesain bukan hanya untuk meloloskan data ke dalam sistem API, melainkan juga untuk bertahan dari gugatan hukum pabean atau tuduhan deforestasi di pengadilan Uni Eropa melalui pendekatan pembuktian ilmiah mutlak (*Indisputable Scientific & Legal Evidence*):

### A. Non-Repudiation Bukti Digital (Rantai Kustodi Kriptografis)
Sistem mengunci hubungan spasial antara berkas gambar satelit (GeoTIFF) dan batas kepemilikan lahan (GeoJSON) secara matematis:
1.  Berkas GeoJSON dianalisis, disterilisasi topologinya, lalu dikunci nilai hash SHA-256-nya.
2.  Nilai hash GeoJSON tersebut disuntikkan langsung ke dalam tag metadata internal berkas GeoTIFF (`LINKED_VECTOR_HASH`) sebelum file citra tersebut disegel kembali.
3.  Perubahan sekecil 1 milimeter pada koordinat batas lahan atau pengeditan piksel raster secara ilegal akan memutus rantai hash ini secara total, menandakan adanya manipulasi data pasca-audit.

### B. eIDAS Trusted Timestamping (RFC 3161 DER Compliance)
Stempel waktu lokal dari *system clock* komputer hulu sangat mudah dipalsukan melalui teknik manipulasi tanggal mundur (*backdating*). Untuk mengatasinya, sistem menyusun kueri biner bertenaga **ASN.1 DER-encoded request** murni sesuai standar RFC 3161. Kueri dikirim langsung ke Qualified Trust Service Provider (QTSP) global untuk memperoleh berkas `.tsr`. Token biner ini memuat waktu UTC resmi yang tersinkronisasi langsung dengan jam atom global, menjadikannya bukti digital yang diakui secara sah oleh seluruh institusi peradilan Eropa.

### C. Algoritma Determinis Tanpa Bias Random (Reprodusibilitas Mutlak)
Guna menjamin kepatuhan *EU AI Act* dan keterbukaan audit ilmiah, seluruh algoritma forensik di dalam sistem ini (baik pencocokan kurva replanting DTW maupun deteksi El Niño) dibangun menggunakan persamaan matematika deterministik murni. Sistem **menghilangkan penggunaan generator acak (`np.random`)**. Hasil audit yang dijalankan hari ini akan selalu menghasilkan nilai desimal yang sama persis jika dijalankan ulang oleh auditor independen Uni Eropa di Brussels lima tahun ke depan.

### D. Transparansi Skor Integritas (Explainable AI - XAI)
Sistem menolak konsep AI kotak hitam (*Black-Box AI*). Peta probabilitas segmentasi AI tidak langsung diekspor sebagai keputusan biner babi buta, melainkan disajikan dalam bentuk gradasi keyakinan murni di **Codes 2 - Blok 4**. Setiap keputusan mitigasi atau kegagalan kepatuhan didokumentasikan dengan persentase kecocokan matematika dan homogenitas tekstur fisik tanah rill.

---
