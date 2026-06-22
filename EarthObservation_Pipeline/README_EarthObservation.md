# Inhu GeoAI — Sistem Kepatuhan Spasial-Legal & Keterlacakan Rantai Pasok Terpadu EUDR

Sistem verifikasi kepatuhan terpadu (*Unified Compliance Verification System*) berbasis kecerdasan buatan geospasial (GeoAI) dan penjaminan administrasi hukum hulu untuk pembelaan kargo ekspor Crude Palm Oil (CPO) Indonesia. Sistem ini dirancang untuk memenuhi secara kumulatif ketentuan uji tuntas pabean Uni Eropa di bawah European Union Deforestation Regulation (EUDR).

### 🛡️ KARTU IDENTITAS KEPATUHAN SISTEM (*SYSTEM COMPLIANCE CARD*)

```
┌────────────────────────────────────────────────────────────────────────┐
│  OPERATOR IDENTIFIER   : ID-EORI-2026-SAWIT-INHU-01                    │
│  REGULATORY FRAMEWORK  : Regulation (EU) 2023/1115 & (EU) 2025/2650    │
│  API SCHEMA SPEC       : TRACES NT M2M JSON-LD v2026.2                 │
│  CRYPTOGRAPHIC ENGINE  : eIDAS Trusted Timestamping (RFC 3161 DER)     │
│  RISK CLASSIFICATION   : Standard-Risk Due Diligence Protocol          │
│  GEOGRAPHIC SCOPE      : Indragiri Hulu, Riau, Republic of Indonesia   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ DAFTAR ISI

1. [Deskripsi Proyek & Demarkasi Regulasi]
2. [Arsitektur Pipeline & Analisis Spasial]
3. [Administrasi Hukum & Integrasi API]
4. [Alur Validasi & Keamanan Kriptografis (eIDAS Standard)]
5. [Prasyarat Teknis & Panduan Instalasi]
6. [Siklus Eksekusi Produksi (Execution Flow)]
7. [Struktur Berkas & Bukti Akhir (Output Archive)]
8. [Atribusi & Batas Liabilitas Hukum]

---

## ⚖️ DESKRIPSI PROYEK & DEMARKASI REGULASI

### 1. Landasan Hukum EUDR & Batas Waktu Temporal (*Cut-off Date*)
Proyek ini dikembangkan sebagai respon teknis dan hukum terhadap pemberlakuan Regulation (EU) 2023/1115 dan amandemen penundaan administratif Regulation (EU) 2025/2650. Meskipun tenggat waktu kewajiban administratif diperpanjang hingga **30 Desember 2026** untuk perusahaan non-SME dan **30 Juni 2027** untuk SME, batas waktu temporal (*cut-off date*) kelayakan lahan tetap dikunci mati per **31 Desember 2020**. Komoditas yang diproduksi dari lahan yang mengalami deforestasi setelah tanggal pembatasan tersebut selamanya dilarang memasuki pasar tunggal Uni Eropa.

### 2. Doktrin Tiga Syarat Kumulatif Kepatuhan (Pasal 3)
Sistem orkestrasi ini memproses data hulu untuk membuktikan secara serempak gerbang logika kepatuhan (AND-Gate) yang diamanatkan dalam Pasal 3 EUDR:

$$\text{Compliance} = D_f \land L_g \land D_{\text{DDS}}$$

*   **$D_f$ (Deforestation-free - Pasal 3(a)):** Komoditas relevan diproduksi di lahan yang bebas dari deforestasi pasca 31 Desember 2020, serta tidak memicu degradasi struktural hutan primer.
*   **$L_g$ (Legality - Pasal 3(b)):** Komoditas diproduksi sesuai dengan hukum positif yang berlaku di negara produsen (Indonesia). Sistem menyaring 5 pilar legalitas nasional: Hak Guna Usaha (HGU), Nomor Induk Berusaha (NIB), dokumen pengelolaan lingkungan (AMDAL/UKL-UPL/SPPL), persetujuan masyarakat adat (FPIC), dan kepatuhan fiskal daerah.
*   **$D_{\text{DDS}}$ (DDS Coverage - Pasal 3(c)):** Pengapalan wajib dilindungi oleh dokumen Pernyataan Uji Tuntas (*Due Diligence Statement*) aktif yang terdaftar secara sah pada portal pabean TRACES NT.

### 3. Protokol Uji Tuntas untuk Standard-Risk Country (Pasal 29)
Indonesia diklasifikasikan sebagai wilayah risiko standar (*standard-risk country*) bersama mayoritas negara produsen kelapa sawit global. Status risiko standar ini mengimplikasikan kewajiban operasional penuh yang tidak dapat dihindari:
*   **Tanpa Hak Pengecualian (*No Waiver*):** Operator dilarang menggunakan jalur cepat (*Simplified Due Diligence*) yang hanya diperuntukkan bagi komoditas dari wilayah risiko rendah (*low-risk country*).
*   **Kewajiban Penilaian Risiko (*Mandatory Risk Assessment*):** Setiap plot lahan wajib melalui proses asesmen risiko komprehensif (Pasal 10) mencakup evaluasi stabilitas kanopi satelit, fusi sensor menembus awan, dan pembuktian legalitas hulu.
*   **Tindakan Mitigasi Aktif (*Active Mitigation*):** Risiko non-negligible wajib dimitigasi secara aktif, dicatat secara transparan di dalam dokumen DDS, dan diverifikasi melalui audit visual temporal secara berkala.

---

## 🛠️ ARSITEKTUR PIPELINE & ANALISIS SPASIAL (CODES 1-3)

Pipeline pengolahan data dirancang secara berjenjang (*tiered-architecture*) untuk memproses telemetri spasial hulu dari satelit Copernicus menjadi bukti digital yang terverifikasi dan memenuhi standar pabean Uni Eropa.

```
[CDSE OpenEO API] ────► [CODES 1: Ingestion & Fusion] ────► Master 6-Band GeoTIFF
                                                                 │
[eIDAS TSR Token] ◄──── [CODES 2: SAM 2 & Topology]   ◄──── Semantic Prob Map
                                                                 │
[Deterministic S-Curve] ◄── [CODES 3: Temporal & Change] ◄── Cleaned 2D GeoJSON
                                                                 │
[DDS JSON-LD v2026.2] ◄─── [CODES 4: Legality & M2M]   ◄── Temporal Profile CSV
```

---

### **CODES 1: Advanced Data Ingestion & Cloud-Clearing (FUSION S1/S2)**
Modul ini bertanggung jawab membangun koneksi asinkron ke server federasi Copernicus Data Space Ecosystem (CDSE) untuk melakukan ekstraksi citra multitemporal bebas awan.

*   **Penyaringan Atmosfer & Reducer Berjenjang:**
    *   **Baseline Lock (Q4 2020):** Menggunakan rentang temporal Oktober–Desember 2020. Di Riau, kuartal ini merupakan puncak curah hujan tinggi yang menyebabkan tutupan awan persisten (*persistent tropical cloud cover*). Sistem menerapkan filter awan berbasis SCL (*Scene Classification Layer*) diikuti dengan **Quantile Reducer P10 (10th Percentile)**. Metode ini berhasil mengisolasi reflektansi vegetasi terbersih dari kontaminasi kabut (*haze*) dan bayangan awan (*cloud shadows*) yang sering lolos dari algoritma deteksi standar.
    *   **Ongoing Stack (Mei 2026):** Rentang temporal Februari–Mei 2026 diproses menggunakan **Median Reducer**. Rentang waktu yang lebih panjang memungkinkan pemanfaatan nilai tengah (*central tendency*) kesehatan kanopi sawit tanpa bias outlier musiman.
*   **Fusi Sensor Aktif (Active Microwave S1 GRD):**
    *   Untuk mengatasi keterbatasan sensor optik tradisional di wilayah tropis curam, sistem menyuntikkan data polarisasi VH dan VV dari radar Sentinel-1.
    *   Hamburan balik (*backscatter*) radar diproses melalui koreksi radiometrik medan (*Radiometric Terrain Correction* - RTC) terikat model elevasi digital **Copernicus DEM 30m (`COPERNICUS_30`)** untuk memotong gangguan bayangan radar (*radar shadow*).
    *   Tekstur radar disatukan ke dalam kanal RGB *False Color Composite* (FCC) Sentinel-2 untuk menonjolkan kerapatan bio-fisik kelapa sawit secara visual.

---

### **CODES 2: SAM 2 & Foundation Models for Precision Mapping**
Modul pemrosesan vektor untuk memetakan batas fisik blok konsesi lahan pertanian hulu secara presisi (*parcel-level delineation*) menggunakan model fondasi segmentasi AI.

*   **Semantic Classification & Soft-Probability (Prithvi-v2):**
    *   Citra masukan 6-band spektral ("Prithvi-Ready") diklasifikasikan menggunakan arsitektur deep learning *Prithvi-v2* dari IBM/NASA dengan LoRA Adapter terlatih khusus karakteristik kelapa sawit tropis Riau.
    *   Sistem memisahkan kelas vegetasi rapat (Hutan Primer), Lahan Terbuka, dan Blok Perkebunan Kelapa Sawit. Probabilitas murni sawit (*soft-probability*) diekstraksi ke dalam Band 2 dari berkas peta probabilitas semantik.
*   **Topological Sterilization (Douglas-Peucker 1.5m):**
    *   Vektor mentah hasil klasifikasi diubah menjadi poligon, ditransformasikan ke sistem proyeksi metrik lokal **UTM Zona 47N (EPSG:32647)** untuk perhitungan area bebas bias, lalu dosterilisasi melalui tiga tahap:
        1.  **Sliver Removal:** Poligon kecil bernilai area $< 0.1$ Hektar ($1000\text{ m}^2$) dihapus untuk menyaring noise sensor.
        2.  **Douglas-Peucker Simplification:** Koordinat titik batas disederhanakan menggunakan toleransi spasial ketat **1.5 meter**. Batas ini dioptimalkan untuk menjaga akurasi kelokan batas fisik lahan riil serta memangkas kelebihan vertex (*vertex buffer layout*) agar lolos batas maksimal 10.000 titik per poligon pabean TRACES NT.
        3.  **Topology Fix:** Penerapan operasi spasial `buffer(0)` untuk menghilangkan *self-intersection* (garis batas yang melilit) dan tumpang tindih (*overlap*) antar poligon tetangga secara instan.
*   **Enforcement Koordinat Murni 2D WGS-84 (RFC 7946):**
    *   Sistem mentransformasikan kembali koordinat hasil simplifikasi ke proyeksi geografis **WGS-84 (EPSG:4326)**.
    *   Fungsi internal `force_geometry_2d()` membedah geometri poligon dan secara mutlak membuang koordinat dimensi Z (3D). Langkah ini krusial karena mesin asimilasi pabean Eropa akan menolak otomatis (*hard rejection*) berkas spasial yang mengandung koordinat 3D.

---

### **CODES 3: Bio-Temporal & Change Detection Analysis**
Modul forensik perubahan lahan secara runtun waktu (*time-series analysis*) untuk membuktikan kestabilan tutupan lahan pertanian pasca *cut-off date*.

```
[CDSE Server] ──(Zonal Stats Mean)──► JSON [[date, [values]], ...]
                                               │
                                 (Fallback Multi-Format Parser)
                                               │
[Temporal CSV Profile] ◄──(Interpolation)───[clean_and_extract_value()]
```

*   **Robust Multi-Format Parser (`parse_openeo_json_to_csv`):**
    *   Untuk mencegah kegagalan eksekusi (*crash*) akibat pembaruan tidak terencana pada format respons API OpenEO CDSE, parser temporal kami dilengkapi penanganan tiga tingkat (*multi-format fallback*):
        *   **Skema 1:** Standard openEO results format (`{"results": [[date, [values]], ...]}`).
        *   **Skema 2:** GeoJSON FeatureCollection format (nilai runtun waktu bersarang di dalam atribut *properties* fitur).
        *   **Skema 3:** Flat Dict / Timeseries Mapping format (`{"timeseries": {"date": [values]}}`).
    *   **Nested List Decap (`clean_and_extract_value`):** openEO merepresentasikan nilai multi-band sebagai list biner (misal: `[0.81]`) meskipun hanya ada satu indeks band yang diproses. Penganalisis kami mendeteksi tipe data terbungkus (*nested list*) secara aman, mengurai lapisan list luar, mengonversi nilai ke float murni, dan menyaring nilai negatif sebelum data dimasukkan ke dalam algoritma interpolasi linier Pandas.
*   **Eliminasi False Positive Alarm:**
    *   **Climate Stress Defense (El Niño Mitigation):** Perhitungan korelasi Pearson jendela lokal (*windowed local Pearson correlation*) pada kuartal anomali kering (Mid-2023) membuktikan bahwa penurunan kehijauan indeks NDVI di lapangan sinkron secara dinamis dengan defisit air tanah akibat kekeringan ekstrim, bukan akibat pembalakan hutan.
    *   **Replanting Cycle Verification (S-Curve Matching):** Menolak tuduhan deforestasi liar saat siklus tanam ulang kebun sawit legal dengan mencocokkan trajektori pemulihan NDVI pasca-penebangan (*clear-cutting*) menggunakan **Sigmoidal Logistic Growth S-Curve** deterministik dan perhitungan jarak Dynamic Time Warping (DTW) dengan batas aman $\le 0.18$.
*   **Sub-Pixel Vegetation Fraction (LSMA Analysis):**
    *   Melacak pembukaan jalan sarat (*logging roads*) di bawah kanopi hutan menggunakan dekomposisi sub-piksel *Linear Spectral Mixture Analysis* (LSMA).
    *   Membagi satu piksel Sentinel-2 menjadi tiga fraksi murni (*endmembers*): Daun Hijau Aktif (GV), Tanah Terbuka (Soil), dan Vegetasi Non-Fotosintetik / Kayu Mati (NPV). Lonjakan fraksi NPV $\ge 50\%$ secara instan mengonfirmasi adanya penebangan struktural di bawah naungan kanopi.
	
---

## 🔐 ALUR VALIDASI & KEAMANAN KRIPTOGRAFIS (eIDAS STANDARD)

Sistem mengimplementasikan skema rantai pengawasan digital (*cryptographic chain-of-custody*) untuk menjamin bahwa data spasial dan laporan administratif tidak dapat dimanipulasi pasca-audit (*non-repudiation*) sesuai regulasi eIDAS Uni Eropa.

```
[Cleaned GeoJSON] ───(SHA-256 Hash)───► [ASN.1 DER Builder] ───► [DigiCert QTSP]
                                                                        │
[COG master raster] ◄──(update_tags)──── [Linked Hash Injection] ◄─── (.tsr Token)
```

### 1. Kueri Biner ASN.1 DER-Encoded (eIDAS Compliance)
Stempel waktu digital berbasis jam lokal sistem sangat rentan terhadap manipulasi waktu mundur (*backdating*). Untuk mengatasinya, kelas `eIDASTimeStampAuthority` membangun kueri stempel waktu biner resmi berstandar **RFC 3161 ASN.1 DER-encoded**:
*   **Struktur Payload Kueri:**
    *   **Version:** INTEGER `1`.
    *   **MessageImprint:** SEQUENCE berisi *AlgorithmIdentifier* (mengunci OID SHA-256: `2.16.840.1.101.3.4.2.1` tanpa parameter tambahan/NULL) dan *hashedMessage* berupa nilai biner 32-byte hash GeoJSON.
    *   **certReq:** BOOLEAN `True` untuk memaksa server QTSP (*Qualified Trust Service Provider*) menyertakan sertifikat x509 rantai kepercayaan Uni Eropa di dalam respons.
*   **Transmisi & Penyegelan (.tsr):**
    *   Payload biner dikirimkan melalui HTTP POST menggunakan header `"Content-Type: application/timestamp-query"` ke server QTSP (default: DigiCert).
    *   Respons biner yang diterima disimpan sebagai token stempel waktu elektronik mandiri `.tsr` (*Time Stamp Response*) di Google Drive.

### 2. Cross-Linked Integrity Seal (Penyegelan Silang)
Sistem mengunci keterkaitan antara berkas spasial raster dengan vektor melalui injeksi metadata silang menggunakan pustaka `rasterio`:
*   Hash SHA-256 dari berkas vektor `Cleaned_EUDR_Polygons_2026.geojson` dihitung.
*   Nilai hash vektor tersebut disuntikkan secara permanen ke dalam tag internal metadata berkas raster master `Prithvi_Ongoing_2026_COG.tif` menggunakan operasi asinkron `dst.update_tags(LINKED_VECTOR_HASH=...)`.
*   Setelah tag internal disematkan, hash akhir dari berkas raster dihitung ulang untuk membentuk basis verifikasi silang pada sertifikat digital `EUDR_Final_Certificate_2026.json`. Modifikasi 1-bit saja pada berkas raster atau GeoJSON akan secara otomatis merusak kecocokan hash silang ini.

### 3. Immutable Transaction Ledger (Buku Besar Transaksi)
*   Setiap langkah penilaian risiko spasial, validasi dokumen hulu, hingga penerimaan nomor registrasi pabean URN dari Brussel dicatat secara permanen ke dalam berkas `Immutable_Audit_Ledger.jsonl`.
*   Sistem mencatat riwayat transaksi secara *append-only* (tanpa izin hapus/modifikasi). Integritas dari seluruh buku besar transaksi ini dilindungi secara total dengan menghitung hash SHA-256 keseluruhan berkas ledger yang ditampilkan secara transparan pada bagian bawah laporan audit HTML eksekutif.

---

## 💻 PRASYARAT TEKNIS & PANDUAN INSTALASI

### 1. Persyaratan Sistem
*   **Sistem Operasi:** Google Colab Environment / Linux (Ubuntu $\ge$ 20.04) / macOS.
*   **Versi Python:** Python $\ge$ 3.10.
*   **Pustaka Python Utama (`requirements.txt`):**
    ```text
    openeo>=0.30.0
    rasterio>=1.4.0
    geopandas>=0.14.0
    numpy>=2.1.0
    pydantic>=2.12.0
    scipy>=1.12.0
    matplotlib>=3.10.0
    shapely>=2.0.0
    pandas>=2.2.0
    nest-asyncio>=1.6.0
    ```

### 2. Konfigurasi Folder Google Drive
Sistem menggunakan Google Drive sebagai media penyimpanan persisten (*persistent storage*) untuk memfasilitasi audit jarak jauh dan menjaga ketersediaan temuan spasial. Jalur absolut direktori kerja ditetapkan pada:
`/content/drive/MyDrive/GeoAI_EUDR_2026/`

Setelah Google Drive terhubung, buat sub-direktori berikut menggunakan terminal atau antarmuka Colab:
*   `/Codes_4_Outputs/` (Penyimpanan ledger transaksi hulu).
*   `/Codes_4_Outputs/DDS_Archive_2026/` (Arsip payload JSON-LD TRACES NT).
*   `/Codes_4_Outputs/EU_Official_Receipts/` (Penyimpanan berkas tanda terima resmi URN dari Brussel).

### 3. Integrasi Kredensial CDSE Copernicus & Secrets Colab
*   Sistem memanfaatkan server federasi openEO CDSE. Anda wajib memiliki akun aktif di portal [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/).
*   Untuk keamanan M2M API Gateway, jangan pernah menuliskan *Client ID* atau *Client Secret* secara langsung di dalam kode (*hardcoded*).
*   **Langkah Konfigurasi Kredensial di Google Colab:**
    1.  Buka panel navigasi samping kiri di Google Colab Notebook Anda.
    2.  Klik ikon kunci 🔑 (**Secrets**).
    3.  Tambahkan dua baris kunci rahasia baru berikut:
        *   Nama Kunci: `EUDR_CLIENT_ID` -> Masukkan Client ID M2M TRACES NT Anda.
        *   Nama Kunci: `EUDR_CLIENT_SECRET` -> Masukkan Client Secret OAuth 2.0 Anda.
    4.  Aktifkan tombol geser izin akses notebook (*Notebook Access*) untuk kedua kunci rahasia tersebut agar modul `google.colab.userdata` dapat menyerap nilai secara aman saat runtime berjalan.
	
---

## 🔄 SIKLUS EKSEKUSI PRODUKSI (EXECUTION FLOW)

Sistem dirancang untuk dieksekusi secara berurutan (*sequential pipeline*) mulai dari akuisisi data fisik hingga penerbitan dokumen pabean akhir.

```
Step 1: CODES 1 Ingestion ──► Step 2: CODES 2 SAM Delineation ──► Step 3: Topology Sanitization
                                                                           │
Step 6: HTML Reporting   ◄── Step 5: CODES 4 M2M Transmission ◄── Step 4: CODES 3 Temporal Audit
```

### 1. Urutan Eksekusi Manual (Step-by-Step)
Untuk menjalankan pengujian mandiri per blok, eksekusi modul-modul berikut secara berurutan di lingkungan Google Colab Anda:
1.  **Akuisisi & Fusi Sensor (CODES 1):** Jalankan Blok 1 hingga Blok 9 untuk mengunduh, membersihkan awan, melakukan fusi radar, melakukan reproyeksi ke UTM 47N, serta melakukan audit kualitas (QA) data optik hulu.
2.  **Delineasi & Klasifikasi AI (CODES 2):** Jalankan Blok 1 dan Blok 2 untuk memicu klasifikasi semantik *Prithvi-v2* dan menghasilkan poligon mentah *SAM 3*.
3.  **Sanitasi Topologi Spasial (CODES 2 - Blok 3):** Jalankan Blok 3 untuk menyederhanakan vertex batas lahan (1.5m toleransi), membuang koordinat 3D, dan menyimpan berkas `Cleaned_EUDR_Polygons_2026.geojson`.
4.  **Analisis Perubahan Lahan (CODES 3):** Jalankan Blok 1 hingga Blok 5 untuk mengekstrak runtun waktu *zonal statistics*, memicu korelasi iklim (*El Niño Defense*), mencocokkan kurva pertumbuhan sawit muda (*Replanting Defense*), dan menghitung fraksi NPV hulu.

### 2. Pemicu Siklus Produksi Otomatis (Full Cycle Execution)
Untuk menjalankan seluruh transaksi ekspor secara *real-time* dan transaksional, panggil pemicu asinkron utama di **Codes 4 — Blok 5**:
```python
import asyncio
# Memulai orkestrasi otomatis dari verifikasi legalitas hulu hingga M2M TRACES NT
await run_production_compliance_cycle()
```
Fungsi di atas secara otomatis mengoordinasikan:
1.  Penyaringan izin administratif hulu terintegrasi ISPO menggunakan `LegalVerificationEngine`.
2.  Penentuan geolokasi otomatis berbasis luas plot (Centroid vs. Poligon 2D penuh).
3.  Penyusunan dokumen DDS JSON-LD v2 dan penyimpanan ledger transaksi hulu.
4.  Transmisi M2M OAuth 2.0 ke portal pabean TRACES NT.
5.  Pembaruan dasbor HTML interaktif eksekutif.

---

## 📂 STRUKTUR BERKAS & BUKTI AKHIR (OUTPUT ARCHIVE)

Setelah seluruh siklus kepatuhan dieksekusi sempurna, Google Drive Anda akan menyimpan kumpulan berkas bukti digital berlapis (*defensive evidence package*) sebagai berikut:

```
📂 /content/drive/MyDrive/GeoAI_EUDR_2026/
 ├── 📄 Cleaned_EUDR_Polygons_2026.geojson  <-- Vektor murni 2D WGS-84 steril topologi
 ├── 📄 Prithvi_Ongoing_2026_COG.tif        <-- Master raster COG disisipi hash vektor hulu
 ├── 📄 EUDR_eIDAS_Timestamp.tsr            <-- TSR biner token stempel waktu RFC 3161
 ├── 📄 EUDR_Final_Certificate_2026.json    <-- Sertifikat kripto rantai pengawasan digital
 └── 📂 Codes_4_Outputs/
      ├── 📄 Immutable_Audit_Ledger.jsonl   <-- Buku besar log transaksi append-only hulu
      ├── 📄 EUDR_Final_Report_2026.html    <-- Dasbor interaktif laporan audit HTML
      ├── 📂 DDS_Archive_2026/
      │    └── 📄 DDS_EUDR-2026-XXXX.json   <-- Payload JSON-LD legalitas & polygon riil
      └── 📂 EU_Official_Receipts/
           └── 📄 RECEIPT_SANDBOX_XXXX.json <-- Tanda terima resmi URN pabean Eropa
```

---

## ⚖️ ATRIBUSI & BATAS LIABILITAS HUKUM

### 1. Sistem Pendukung Keputusan (*Decision-Support System Status*)
Seluruh komponen analisis algoritma penginderaan jauh (*remote sensing telemetry*), klasifikasi semantik *Prithvi-v2*, delineasi *SAM 3*, serta visualisasi peta di dalam sistem GeoAI ini diposisikan murni sebagai alat bantu analisis pendukung keputusan (*Decision-Support System* - DSS). Sistem ini dirancang untuk mendeteksi anomali fisik permukaan tanah secara probabilistik, bukan sebagai penjamin mutlak terbebas dari kesalahan klasifikasi satelit atau bias atmosferik.

### 2. Batas Tanggung Jawab Hukum (*Limitation of Liability*)
*   Penyedia jasa teknologi GeoAI tidak memberikan jaminan absolut bahwa seluruh klasifikasi spasial terbebas dari galat (*false positive / false negative*) akibat keterbatasan spektral sensor, tutupan awan tropis ekstrim, atau perubahan dinamika vegetasi non-antropogenik.
*   Keputusan akhir pengajuan berkas DDS ke portal TRACES NT Uni Eropa sepenuhnya berada di bawah tanggung jawab operasional dan hukum dari Operator / Eksportir yang bersangkutan.
*   Penyedia jasa teknologi GeoAI dibebaskan secara mutlak dari segala bentuk tuntutan ganti rugi atas kerugian tidak langsung, kehilangan potensi keuntungan bisnis, atau denda administratif yang dijatuhkan oleh otoritas kepabeanan Uni Eropa akibat kesalahan penafsiran data spasial hulu.

---

# Rangkuman Seluruh Bagian Dokumentasi:

1.  **Bagian 1 — Judul & Identitas Sistem:** Menyediakan identitas operasional (EORI, skema API, tingkat eIDAS) yang disesuaikan secara dinamis.
2.  **Bagian 2 — Daftar Isi:** Navigasi cepat penelaahan berkas.
3.  **Bagian 3 — Deskripsi Proyek & Demarkasi Regulasi:** Menjelaskan korelasi teknis dengan Pasal 3, Pasal 9, dan Pasal 10 EUDR, serta pemosisian Indonesia sebagai Standard-Risk Country.
4.  **Bagian 4 — Arsitektur Pipeline & Analisis Spasial (Codes 1-3):** Menjabarkan justifikasi ilmiah reducer P10 vs Median, batas threshold JRC `-0.06`, penjaminan koordinat murni 2D, parser multi-format CDSE, serta mitigasi bias fenologi hulu.
5.  **Bagian 5 — Alur Validasi & Keamanan Kriptografis (eIDAS Standard):** Detail teknis pembangunan kueri biner ASN.1 DER-encoded untuk TSR stempel waktu eksternal, penyegelan silang GeoTIFF-GeoJSON, dan integritas ledger.
6.  **Bagian 6 — Prasyarat Teknis & Panduan Instalasi:** Kebutuhan sistem, pustaka Python, struktur folder Drive, dan tata cara konfigurasi kunci rahasia (*secrets*) Colab.
7.  **Bagian 7 — Siklus Eksekusi Produksi (Execution Flow):** Langkah manual runtun waktu prapemrosesan serta pemicu asinkron utama siklus otomatis hulu-hilir.
8.  **Bagian 8 — Struktur Berkas & Bukti Akhir (Output Archive):** Pemetaan nama-nama berkas bukti digital berlapis yang aman di Google Drive.
9.  **Bagian 9 — Atribusi & Batas Liabilitas Hukum:** Klausul pembatasan tanggung jawab hukum yang meluruskan pemosisian AI sebagai sistem pendukung keputusan (*Decision-Support System*).
