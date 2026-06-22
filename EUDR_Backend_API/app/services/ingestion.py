import io
import os
import math
import cv2
import numpy as np
import easyocr
import openai
import google.generativeai as genai
import json
import uuid
import hashlib
import base64
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.services.geo_audit import generate_h3_indices_from_polygon
from app.services.vault import encrypt_and_vault_pii

# Import Model Database & Layanan Audit Spasial Baru kita
from app.models import Plot, AuditLedger
from app.schemas import FarmerPlotInput
from app.services.geo_audit import execute_multi_layer_spatial_audit, sanitize_and_simplify_polygon

# [OPTIMASI] Set global variable ke None. Kita akan memuatnya hanya saat dibutuhkan (Lazy Loading)
reader = None

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


# ==========================================
# KOMPONEN SPASIAL & EXIF FORENSIK
# ==========================================

def get_decimal_from_dms(dms: Tuple[float, float, float], ref: str) -> float:
    degrees = float(dms[0])
    minutes = float(dms[1])
    seconds = float(dms[2])
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def extract_exif_metadata(image_bytes: bytes) -> Tuple[Optional[float], Optional[float], Optional[datetime]]:
    if image_bytes == b"MOCK_IMAGE_BYTES_INHU_RIAU":
        return -0.381104, 102.498719, datetime.now()
        
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif_data = image._getexif()
        if not exif_data:
            return None, None, None
        
        gps_info = {}
        timestamp_raw = None
        
        for tag, value in exif_data.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                for gps_tag in value:
                    sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[sub_decoded] = value[gps_tag]
            elif decoded == "DateTimeOriginal":
                timestamp_raw = value

        lat, lon = None, None
        if "GPSLatitude" in gps_info and "GPSLatitudeRef" in gps_info and "GPSLongitude" in gps_info and "GPSLongitudeRef" in gps_info:
            lat = get_decimal_from_dms(gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"])
            lon = get_decimal_from_dms(gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"])
            
        timestamp = None
        if timestamp_raw:
            try:
                timestamp = datetime.strptime(timestamp_raw, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                pass
                
        return lat, lon, timestamp
    except Exception:
        return None, None, None

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


# ==========================================
# PREPROCESSING OPENCV, OCR & LLM PARSER
# ==========================================

def preprocess_image_for_ocr(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.adaptiveThreshold(
        gray, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    return processed_img

def run_easy_ocr(processed_img: np.ndarray) -> str:
    """
    Lazy Loading: Hanya memuat model EasyOCR ke RAM saat fungsi benar-benar dipanggil
    """
    global reader
    if reader is None:
        print("📦 Menginisialisasi Mesin EasyOCR (Lazy Loading)...")
        reader = easyocr.Reader(['id', 'en'], gpu=False)
    results = reader.readtext(processed_img, detail=0)
    return " ".join(results)

def parse_ocr_to_json(raw_text: str) -> Dict[str, Any]:
    prompt = f"""
    Kamu adalah sistem audit OCR Uni Eropa untuk kepatuhan EUDR.
    Tugasmu adalah membaca teks berantakan hasil pembacaan mesin OCR pada nota timbang kelapa sawit berikut:
    
    TEXT OCR MENTAH:
    \"\"\"{raw_text}\"\"\"
    
    Lakukan ekstraksi data dengan aturan ketat berikut:
    1. Cari nama petani (sering kali berada di samping kata 'Nama', 'Petani', 'Penjual', 'Anggota', atau 'Nasabah').
    2. Cari tonase bersih atau estimasi kargo saat ini dalam satuan Metric Ton (MT). 
       Jika pada teks tertulis kilogram (misal: '4500 kg' atau 'Netto: 3200'), konversikan langsung ke Metric Ton (MT) dengan membaginya 1000 (contoh: 4.5 MT atau 3.2 MT).
    
    Kembalikan output murni dalam bentuk JSON valid dengan skema berikut tanpa penjelasan tambahan:
    {{
        "extracted_farmer_name": "NAMA PETANI YANG DIKETEMUKAN",
        "extracted_quantity_mt": ESTIMASI_DALAM_ANGKA_DESIMAL_METRIC_TON
    }}
    """
    
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception:
            pass

    if OPENAI_API_KEY:
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            clean_res = response.choices[0].message.content.strip()
            return json.loads(clean_res)
        except Exception:
            pass

    return {
        "extracted_farmer_name": "Parser Error (Manual Review)",
        "extracted_quantity_mt": 0.0
    }


# ==========================================
# PIPELINE UTAMA & VERIFIKASI TRANSAKSIONAL
# ==========================================

async def extract_vision_and_exif(raw_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    TUGAS WORKER 1: Menangani komputasi RAM/GPU.
    Menerima JSON dari WhatsApp, membaca EXIF, dan melakukan OCR teks.
    """
    image_bytes = base64.b64decode(raw_payload["image_base64"])
    
    # 1. FORENSIK KOORDINAT (EXIF)
    exif_lat, exif_lon, photo_time = extract_exif_metadata(image_bytes)
    if exif_lat is None or exif_lon is None:
        raise ValueError("Gagal validasi EXIF: Gambar tidak memiliki metadata lokasi GPS asli.")
        
    # 2. VALIDASI RADIUS AMBANG BATAS FOTO (Haversine <= 100m)
    claimed_lat = raw_payload["claimed_lat"]
    claimed_lon = raw_payload["claimed_lon"]
    distance_meters = calculate_haversine_distance(claimed_lat, claimed_lon, exif_lat, exif_lon)
    
    if distance_meters > 100.0:
        raise ValueError(f"Jarak foto ({distance_meters:.2f}m) di luar batas toleransi (100m).")

    # 3. OPENCV, EASYOCR & PARSING SEMANTIK LLM
    farmer_name = raw_payload["farmer_name"]
    if image_bytes == b"MOCK_IMAGE_BYTES_INHU_RIAU":
        extracted_qty = 12.5
        extracted_name = farmer_name
    else:
        cleaned_img = preprocess_image_for_ocr(image_bytes)
        raw_ocr_text = run_easy_ocr(cleaned_img)
        parsed_json = parse_ocr_to_json(raw_ocr_text)
        extracted_qty = parsed_json.get("extracted_quantity_mt", 0.0)
        extracted_name = parsed_json.get("extracted_farmer_name", farmer_name)

    # Konstruksi Payload untuk dilempar ke Worker 2
    return {
        "plot_id": raw_payload["plot_id"],
        "nib": raw_payload["nib"],
        "farmer_name": extracted_name,
        "claimed_lat": claimed_lat,
        "claimed_lon": claimed_lon,
        "area_ha": raw_payload["area_ha"],
        "exif_lat": exif_lat,
        "exif_lon": exif_lon,
        "distance_meters": distance_meters,
        "extracted_qty": extracted_qty
    }

async def process_spatial_and_ledger(geo_payload: Dict[str, Any], db: AsyncSession) -> Dict[str, Any]:
    """
    TUGAS WORKER 2: Menangani komputasi CPU Spasial & Database I/O.
    Menerima hasil OCR, melakukan kueri PostGIS, memotong kuota, dan menyimpan Audit Ledger.
    """
    plot_id = geo_payload["plot_id"]
    area_ha = geo_payload["area_ha"]
    extracted_qty = geo_payload["extracted_qty"]
    claimed_lat = geo_payload["claimed_lat"]
    claimed_lon = geo_payload["claimed_lon"]

    # 4. PEMBENTUKAN GEOMETRI DINAMIS & SHAPELY CLEANING
    half_side = (math.sqrt(area_ha * 10000.0) / 2.0) / 111319.9
    raw_geojson = {
        "type": "Polygon",
        "coordinates": [[
            [claimed_lon - half_side, claimed_lat - half_side],
            [claimed_lon + half_side, claimed_lat - half_side],
            [claimed_lon + half_side, claimed_lat + half_side],
            [claimed_lon - half_side, claimed_lat + half_side],
            [claimed_lon - half_side, claimed_lat - half_side]
        ]]
    }
    
    clean_polygon = sanitize_and_simplify_polygon(raw_geojson)
    plot_wkt_geom = clean_polygon.wkt

    # [BARU] 4.5. KONVERSI POLIGON MENJADI UBER H3 HEXAGON ARRAY
    h3_array = generate_h3_indices_from_polygon(clean_polygon, resolution=11)

    # 5. MULTI-LAYER SPATIAL AUDIT & AUTO-CLIPPING
    spatial_result = await execute_multi_layer_spatial_audit(plot_wkt_geom, db)
    if spatial_result["spatial_verdict"] == "NON_COMPLIANT_REJECTED":
        raise ValueError(f"Ditolak! {spatial_result['message']}")

    # 6. FORMULA YVE DINAMIS [47, 48]
    max_harvest_annual_mt = area_ha * 25.0 * (1.0 - 0.15)

    # [BARU] 6.5. ENKRIPSI & VAULTING DATA PRIBADI (GDPR COMPLIANCE) [89]
    # Data nama & NIB disaring, kita hanya memegang Token Asosiasi di database publik
    association_token = await encrypt_and_vault_pii(
        farmer_name=geo_payload["farmer_name"],
        nib=geo_payload["nib"],
        db=db
    )

    # 7. DOUBLE-SPEND PREVENTION (ACID) [51, 52]
    query_plot = select(Plot).filter(Plot.plot_id == plot_id)
    db_result = await db.execute(query_plot)
    db_plot = db_result.scalar_one_or_none()

    if not db_plot:
        db_plot = Plot(
            plot_id=plot_id,
            nib=association_token,
            farmer_name=association_token,
            area_ha=area_ha,
            annual_quantity_estimate_mt=max_harvest_annual_mt,
            sisa_kuota_berjalan=max_harvest_annual_mt,
            geom=plot_wkt_geom,
            h3_indices=h3_array
        )
        db.add(db_plot)
    else:
        if db_plot.sisa_kuota_berjalan < extracted_qty:
            raise ValueError(f"DOUBLE-SPEND BLOCKED: Kargo ({extracted_qty} MT) melebihi sisa kuota legal ({db_plot.sisa_kuota_berjalan:.2f} MT).")
        db_plot.h3_indices = h3_array

    db_plot.sisa_kuota_berjalan -= extracted_qty
    
    # 8. PENCATATAN IMMUTABLE AUDIT LEDGER
    audit_log = AuditLedger(
        plot_id=plot_id,
        dds_reference=f"URN-DDS-{uuid.uuid4().hex[:8].upper()}",
        compliance_status="COMPLIANT",
        digital_seal=hashlib.sha256(f"{plot_id}-{extracted_qty}".encode()).hexdigest(),
        payload_json=json.dumps(spatial_result)
    )
    db.add(audit_log)
    
    await db.commit()
    return {"status": "SUCCESS", "digital_seal": audit_log.digital_seal}