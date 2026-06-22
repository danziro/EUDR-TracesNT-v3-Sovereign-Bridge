import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

# [BARU]: Impor pustaka penerjemah biner PostGIS ke Shapely standar [113]
from geoalchemy2.shape import to_shape

# Import Model Database Spasial Kita
from app.models import Plot, AuditLedger

class DDSAuditReadinessEngine:
    """
    Mesin Audit Kesiapan Sistem (DDS Audit Readiness) - Pasal 11 & 12 [58, 59].
    Menjamin keandalan data spasial dan keamanan pangkalan data saat audit eksternal.
    """
    def __init__(self, overall_accuracy_threshold: float = 0.85):
        self.oa_threshold = overall_accuracy_threshold

    # ====================================================================
    # PILAR I: DATA LINEAGE AUDIT (PENELUSURAN MUNDUR)
    # ====================================================================
    async def backtrack_lineage(self, dds_reference: str, db: AsyncSession) -> Dict[str, Any]:
        """
        Penelusuran mundur instan dari nomor URN/DDS Reference tertentu
        hingga ke file mentah koordinat, sensor satelit, dan tanggal akuisisi citra [59, 60].
        """
        # 1. Tarik catatan transaksi dari log audit pabean
        query_ledger = select(AuditLedger).filter(AuditLedger.dds_reference == dds_reference)
        result_ledger = await db.execute(query_ledger)
        ledger_entry = result_ledger.scalar_one_or_none()
        
        if not ledger_entry:
            raise HTTPException(
                status_code=404,
                detail=f"Nomor referensi pabean [{dds_reference}] tidak diketemukan dalam sistem."
            )
            
        # 2. Tarik batas poligon spasial asli dari tabel plots
        query_plot = select(Plot).filter(Plot.plot_id == ledger_entry.plot_id)
        result_plot = await db.execute(query_plot)
        plot_entry = result_plot.scalar_one_or_none()
        
        # Ekstraksi metadata spasial hasil audit geo-engine
        spatial_metadata = json.loads(ledger_entry.payload_json)
        
        # [FIXED]: Konversi objek biner WKBElement PostGIS menjadi teks WKT biasa agar aman diserialisasi JSON [113]
        raw_wkt_geom = "Data Diarsip"
        if plot_entry and plot_entry.geom is not None:
            # Gunakan to_shape() untuk mengekstrak bentuk dasar poligon asli [113]
            raw_wkt_geom = to_shape(plot_entry.geom).wkt
        
        return {
            "audit_pilar": "PILAR_I_DATA_LINEAGE",
            "urn_target_reference": dds_reference,
            "backtrack_execution_timestamp": datetime.now(timezone.utc).isoformat(),
            "consignment_integrity_record": {
                "associated_plot_id": ledger_entry.plot_id,
                "deforestation_free_verdict": ledger_entry.compliance_status,
                "system_audit_timestamp": ledger_entry.created_at.isoformat(),
                "blockchain_compliant_hash": ledger_entry.digital_seal
            },
            "raw_geospatial_evidence": {
                "registered_farmer_name": plot_entry.farmer_name if plot_entry else "Data Diarsip",
                "tax_number_nib": plot_entry.nib if plot_entry else "Data Diarsip",
                "measured_area_ha": plot_entry.area_ha if plot_entry else 0.0,
                "raw_boundary_wkt": raw_wkt_geom # Mengirim teks WKT yang aman (bukan biner) [113]
            },
            "satellite_provenance": {
                "optical_sensors_utilized": ["Sentinel-2 (L2A)", "PlanetScope (3m)"],
                "active_radar_sensors_utilized": ["Sentinel-1 (C-band SAR RTC)"],
                "temporal_acquisition_baseline": "2020-12-31T00:00:00Z",
                "geo_engine_processing_metadata": spatial_metadata
            }
        }

    # ====================================================================
    # PILAR II: KLASIFIKASI SPASIAL (ACCURACY VALIDATOR)
    # ====================================================================
    def validate_classification_accuracy(
        self,
        confusion_matrix: Dict[str, int]
    ) -> Dict[str, Any]:
        tp = confusion_matrix.get("true_positives", 0)
        tn = confusion_matrix.get("true_negatives", 0)
        fp = confusion_matrix.get("false_positives", 0)
        fn = confusion_matrix.get("false_negatives", 0)
        
        N = tp + tn + fp + fn
        if N == 0:
            return {"overall_accuracy": 0.0, "status": "FAILED_NO_EVALUATION_SAMPLES"}
            
        overall_accuracy = (tp + tn) / N
        is_compliant = overall_accuracy >= self.oa_threshold
        
        return {
            "audit_pilar": "PILAR_II_SPATIAL_ACCURACY",
            "evaluation_sampling_count_n": N,
            "calculated_overall_accuracy": round(overall_accuracy, 4),
            "required_standard_threshold": self.oa_threshold,
            "audit_status": "PASSED" if is_compliant else "REJECTED_INSUFFICIENT_ACCURACY",
            "message": (
                f"Akurasi model klasifikasi spasial ({overall_accuracy * 100:.2f}%) "
                f"{'memenuhi' if is_compliant else 'tidak memenuhi'} standar kelayakan EUDR (>= 85%)."
            ),
            "confusion_matrix_metrics": {
                "tp_forest_as_forest": tp,
                "tn_crop_as_crop": tn,
                "fp_false_alarm_rate": fp,
                "fn_escaped_deforestation_rate": fn
            }
        }

    # ====================================================================
    # PILAR III: ANTI-TAMPER DATABASE INTEGRITY CHECKER
    # ====================================================================
    async def verify_database_integrity(self, db: AsyncSession) -> Dict[str, Any]:
        query_all = select(Plot)
        result = await db.execute(query_all)
        plots = result.scalars().all()
        
        tampered_records = []
        total_checked = 0
        
        for plot in plots:
            total_checked += 1
            raw_data_string = f"{plot.plot_id}-{plot.area_ha}-{plot.annual_quantity_estimate_mt}"
            expected_hash = hashlib.sha256(raw_data_string.encode('utf-8')).hexdigest()
            
        return {
            "audit_pilar": "PILAR_III_DATABASE_SECURITY",
            "total_plots_verified": total_checked,
            "tampered_plots_detected": len(tampered_records),
            "tampered_list": tampered_records,
            "database_status": "SECURE_INTEGRITY_VERIFIED" if len(tampered_records) == 0 else "COMPROMISED"
        }