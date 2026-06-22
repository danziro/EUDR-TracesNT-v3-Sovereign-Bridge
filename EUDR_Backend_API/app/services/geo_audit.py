import h3
import json
from shapely.geometry import mapping
from shapely.geometry import Polygon, MultiPolygon, shape
from shapely.validation import make_valid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


def sanitize_and_simplify_polygon(geojson_geom: dict) -> Polygon:
    """
    Menggunakan Shapely untuk mensterilkan geometri poligon [25, 26]:
    1. Memperbaiki self-intersection (membentuk angka 8) secara otomatis menggunakan make_valid.
    2. Menghapus duplikasi vertices yang berhimpitan pada jarak < 1 meter.
    3. Menyederhanakan titik sudut menggunakan algoritma Douglas-Peucker (Toleransi 1.5 meter).
    """
    try:
        # Mengubah GeoJSON geom menjadi Shapely object
        poly_shape = shape(geojson_geom)
        
        if not poly_shape.is_valid:
            # Memperbaiki geometri yang melilit/rusak tanpa mengubah koordinat luar
            poly_shape = make_valid(poly_shape)
            
        # Jika hasil perbaikan berupa MultiPolygon, ambil poligon terluas (prioritas lahan utama)
        if poly_shape.geom_type == 'MultiPolygon':
            poly_shape = max(poly_shape.geoms, key=lambda p: p.area)
            
        # Penerapan Algoritma Douglas-Peucker (Toleransi spasial 1.5m untuk efisiensi simpul)
        # 1.5 meter adalah ambang batas maksimal efisiensi pabean TRACES NT
        simplified_shape = poly_shape.simplify(tolerance=0.000015, preserve_topology=True) # ~1.5 meter dalam DD
        
        # Penjaminan cincin koordinat tertutup sempurna (closed-ring)
        if not simplified_shape.exterior.is_closed:
            raise ValueError("Poligon tidak tertutup sempurna.")
            
        return simplified_shape
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Gagal memproses validasi topologi geometri: {str(e)}"
        )

def generate_h3_indices_from_polygon(clean_shape: Polygon, resolution: int = 11) -> list:
    """
    Mengonversi Geometri Poligon menjadi sekumpulan Array ID Uber H3 Hexagon.
    Resolusi 11 setara dengan luas ~2.000 meter persegi (0.2 Hektar) per hexagon.
    """
    try:
        # 1. Konversi Shapely Polygon menjadi GeoJSON standard
        geojson_geom = mapping(clean_shape)
        
        # 2. H3 Polyfill mengharapkan format dictionary khusus
        # Pastikan formatnya sesuai (Polyfill menerima koordinat outer & inner ring)
        geo_dict = {
            'type': geojson_geom['type'],
            'coordinates': geojson_geom['coordinates']
        }
        
        # 3. Hasilkan daftar Hexagon yang menutupi (mengarsir) poligon lahan
        # h3.polyfill mengembalikan set string ID Hexagon (contoh: '8b6530621357fff')
        hexagons = h3.polyfill(geo_dict, resolution, geo_json_conformant=True)
        
        # Jika poligon terlalu kecil hingga lolos dari jaring Resolusi 11,
        # kita ambil titik tengahnya (centroid) sebagai fallback 1 hexagon.
        if not hexagons:
            centroid = clean_shape.centroid
            fallback_hex = h3.geo_to_h3(centroid.y, centroid.x, resolution)
            hexagons = set([fallback_hex])
            
        return list(hexagons)
    
    except Exception as e:
        # Jika gagal, jangan matikan sistem. Kembalikan array kosong (Aman untuk DLQ/Logging)
        from app.logger import log
        log.error("h3_conversion_failed", error=str(e))
        return []

async def execute_multi_layer_spatial_audit(
    plot_geom_wkt: str,
    db: AsyncSession
) -> dict:
    """
    Kueri native PostGIS untuk mengeksekusi matriks prioritas hierarki dokumen hukum (Legal Priority Matrix) [61, 62]:
    1. Cek tumpang tindih terhadap Kawasan Hutan (Prioritas III) dan HGU (Prioritas I).
    2. Jika ada konflik kawasan hutan tanpa sertifikat HGU, picu pemotongan otomatis (Auto-Clipping) dengan buffer 50m.
    3. Validasi sisa luas bersih (Pclean >= 0.5 Ha).
    """
    # Kueri A: Hitung interseksi spasial langsung di dalam mesin PostGIS
    query = text("""
        SELECT 
            -- Cek apakah lahan beririsan dengan Kawasan Hutan Lindung (Prioritas III)
            COALESCE(
                ST_Area(ST_Intersection(ST_GeomFromText(:wkt, 4326), ST_Union(f.geom))), 0
            ) AS area_conflict_forest,
            
            -- Cek apakah lahan dijamin oleh HGU Aktif (Prioritas I)
            COALESCE(
                ST_Area(ST_Intersection(ST_GeomFromText(:wkt, 4326), ST_Union(h.geom))), 0
            ) AS area_covered_hgu,
            
            -- Geometri bersih hasil pemotongan (Pclean = Plahan \ (Pconflict_forest - Phgu))
            ST_AsText(
                ST_Difference(
                    ST_GeomFromText(:wkt, 4326),
                    ST_Buffer(
                        ST_Difference(
                            COALESCE(ST_Union(f.geom), ST_GeomFromText('POLYGON EMPTY', 4326)),
                            COALESCE(ST_Union(h.geom), ST_GeomFromText('POLYGON EMPTY', 4326))
                        ),
                        0.00045 -- Buffer 50 meter dalam derajat desimal untuk antisipasi galat GPS satelit
                    )
                )
            ) AS clean_geometry_wkt
        FROM 
            (SELECT 1) x
        LEFT JOIN kawasan_hutan_prioritas_3 f ON ST_Intersects(ST_GeomFromText(:wkt, 4326), f.geom)
        LEFT JOIN hgu_prioritas_1 h ON ST_Intersects(ST_GeomFromText(:wkt, 4326), h.geom);
    """)
    
    result = await db.execute(query, {"wkt": plot_geom_wkt})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=500, detail="Mesin PostGIS gagal memproses kalkulasi spasial.")
        
    forest_conflict = float(row.area_conflict_forest) * 111319.9**2 # Konversi kasar derajat persegi ke m2
    hgu_coverage = float(row.area_covered_hgu) * 111319.9**2
    clean_wkt = row.clean_geometry_wkt
    
    # Konversi geometri bersih ke Shapely untuk cek luas sisa
    from shapely.wkt import loads
    clean_shape = loads(clean_wkt)
    
    # Hitung luas area bersih dalam hektar (1 Ha = 10,000 m2)
    # Di wilayah tropis khatulistiwa, 1 derajat desimal ~ 111.32 km
    clean_area_ha = (clean_shape.area * 111319.9**2) / 10000.0
    
    # LOGIKA KEPUTUSAN HIERARKI HUKUM (BAB 8.2)
    if forest_conflict == 0:
        # Lahan bersih, tidak ada konflik kawasan hutan
        status = "COMPLIANT_CLEAN"
        action = "APPROVED_FULL"
        message = "Lahan bersih sepenuhnya di luar kawasan hutan lindung."
    elif hgu_coverage >= forest_conflict:
        # Ada tumpang tindih hutan, tapi seluruh area konflik ditutupi oleh sertifikat HGU yang sah (Prioritas I)
        status = "COMPLIANT_WITH_HGU"
        action = "APPROVED_BY_PRIORITY_RULE"
        message = "Tumpang tindih kawasan hutan diabaikan karena dilindungi sertifikat HGU Prioritas I."
    else:
        # Terjadi penyerobotan kawasan hutan tanpa dilandasi dokumen HGU. Picu Auto-Clipping!
        if clean_area_ha >= 0.5:
            # Sisa luasan masih memenuhi syarat batas minimal hutan FAO (>= 0.5 Hektar)
            status = "PARTIAL_COMPLIANT_CLIPPED"
            action = "AUTO_CLIPPED_REGISTERED"
            message = f"Area konflik dipotong otomatis (Buffer 50m). Sisa area bersih ({clean_area_ha:.2f} Ha) didaftarkan ekspor."
        else:
            # Luas sisa terlalu kecil, tidak memenuhi ambang batas minimum pengelolaan lahan legal
            status = "NON_COMPLIANT_REJECTED"
            action = "BLOCK_URN_DDS"
            message = f"Kargo ditolak! Setelah pemotongan area konflik, sisa lahan bersih ({clean_area_ha:.2f} Ha) di bawah batas minimum FAO (0.5 Ha)."
            
    return {
        "spatial_verdict": status,
        "action_taken": action,
        "message": message,
        "clean_area_ha": round(clean_area_ha, 4),
        "clean_geometry_wkt": clean_wkt if status == "PARTIAL_COMPLIANT_CLIPPED" else plot_geom_wkt
    }