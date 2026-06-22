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
├── deliverables_sample/           # [BUKTI FORENSIK] Output steril untuk auditor
│   ├── Cleaned_EUDR_Polygons_2026.geojson
│   ├── DDS_Payload_Ready.jsonld
│   ├── EUDR_Final_Certificate_2026.json
│   └── EUDR_eIDAS_Timestamp.tsr   # <-- Bukti Kriptografi Biner RFC 3161 DER-Encoded
│
├── EarthObservation_Pipeline/     # [THE ATOMS ENGINE] Fisika Satelit & GeoAI
│   ├── GeoAICode_Simulation.ipynb # Mesin fusi radar, optis, dan ZKV
│   └── README_EarthObservation.md # Panduan komputasi satelit
│
├── EUDR_Backend_API/              # [THE BITS ENGINE] Ledger, Kafka, PostGIS & API
│   ├── app/                       # Logika inti (FastAPI, ZKV, eIDAS, Traces M2M)
│   ├── docker/                    # Kontainerisasi infrastruktur
│   └── README_BACKEND.md          # Panduan instalasi dan deployment mikroservis
│
└── eudr_sdk/                      # [PUBLIC SDK] Jembatan Integrasi Eksternal
    ├── eidas_sealer.py            # Klien stempel waktu QTSP eIDAS
    ├── schemas.py                 # Pydantic schema (HGU, NIB, ISPO, GDPR Vault)
    ├── soap_wrapper.py            # Konverter JSON-LD ke TRACES SOAP XML v3
    └── traces_client.py           # Klien transmisi asinkron ke bea cukai Eropa
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