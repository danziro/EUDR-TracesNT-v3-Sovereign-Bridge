# ====================================================================
# PROJECT   : Sovereign RegTech Protocol (EUDR Gateway SDK)
# MODULE    : schemas.py
# STANDARD  : EUDR 2023/1115 Article 9 & 10 | Regulation (EU) 2025/2650
# COMPLIANCE: Indonesian OSS NIB Standard & ISPO Certification Integration
# ====================================================================

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime, timezone

class LegalDocumentsInput(BaseModel):
    """
    Schema input dokumen legalitas sesuai yurisdiksi Indonesia
    dan standar pembuktian hukum pabean Uni Eropa (Pasal 3(b)).
    Mengintegrasikan verifikasi ISPO untuk memperkuat posisi Standard-Risk Country.
    """
    nib: str = Field(
        ...,
        json_schema_extra={"example": "1234567890123"},
        description="Nomor Induk Berusaha (13-digit standard OSS Indonesia)",
    )
    hgu_number: str = Field(
        ...,
        json_schema_extra={"example": "HGU-RI-1402-008"},
        description="Nomor Sertifikat Hak Guna Usaha aktif dari ATR/BPN",
    )
    environmental_permit_type: str = Field(
        ...,
        json_schema_extra={"example": "AMDAL"},
        description="Jenis dokumen lingkungan: AMDAL, UKL-UPL, atau SPPL",
    )
    environmental_permit_number: str = Field(
        ...,
        json_schema_extra={"example": "SK-KLHK-2024-9988"},
        description="Nomor surat keputusan kelayakan/persetujuan lingkungan",
    )
    fpic_verification_status: bool = Field(
        ...,
        description="Pernyataan persetujuan tertulis FPIC dengan masyarakat adat setempat",
    )
    fiscal_tax_clearance: bool = Field(
        ...,
        description="Status pelunasan PBB perkebunan dan pajak ekspor terkait",
    )
    ispo_certificate_number: Optional[str] = Field(
        None,
        json_schema_extra={"example": "ISPO-MUTU-99887"},
        description="Nomor sertifikat ISPO jika tersedia",
    )
    ispo_certification_year: Optional[int] = Field(
        None,
        json_schema_extra={"example": 2024},
        description="Tahun sertifikasi ISPO jika tersedia",
    )

    @field_validator("nib")
    @classmethod
    def validate_nib(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 13:
            raise ValueError(
                "NIB tidak valid. Harus berupa 13 digit angka standar OSS Indonesia."
            )
        return v

    @field_validator("environmental_permit_type")
    @classmethod
    def validate_permit_type(cls, v: str) -> str:
        allowed = ["AMDAL", "UKL-UPL", "SPPL"]
        normalized = v.strip().upper()
        if normalized not in allowed:
            raise ValueError(
                f"Jenis dokumen lingkungan tidak valid. Diperbolehkan: {allowed}"
            )
        return normalized

    @field_validator("ispo_certification_year")
    @classmethod
    def validate_ispo_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            current_year = datetime.now(timezone.utc).year
            if not (2011 <= v <= current_year):
                raise ValueError(
                    f"Tahun sertifikasi ISPO tidak valid. Harus di antara tahun 2011 dan {current_year}."
                )
        return v


class FarmerPlotInput(BaseModel):
    """
    Schema input data terpadu untuk pengajuan orkestrasi audit.
    Mengunci validasi topologi spasial (Titik vs Poligon) berdasarkan luasan.
    """
    plot_id: str = Field(
        ...,
        json_schema_extra={"example": "EUDR-INHU-001"},
        description="Identifier unik poligon atau plot lahan",
    )
    nib: str = Field(
        ...,
        json_schema_extra={"example": "1234567890123"},
        description="Nomor Induk Berusaha (13-digit standard)",
    )
    commodity: str = "Oil Palm"
    latitude: float
    longitude: float
    area_ha: float
    farmer_name: str
    annual_quantity_estimate_mt: float = Field(
        ...,
        json_schema_extra={"example": 50.0},
        description="Estimasi kuantitas panen tahunan dalam metrik ton",
    )
    geojson_polygon_path: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Cleaned_EUDR_Polygons_2026.geojson"},
        description="Jalur absolut berkas GeoJSON keluaran Codes 2 Blok 3",
    )
    legal_documents: LegalDocumentsInput

    @field_validator("latitude", "longitude")
    @classmethod
    def validate_coords(cls, v: float) -> float:
        if v == 0:
            raise ValueError("Koordinat tidak boleh nol (False Geolocation)")
        return v

    @model_validator(mode="after")
    def check_polygon_for_large_plots(self) -> "FarmerPlotInput":
        """
        VALIDATOR HUKUM MANDATORI (EUDR Pasal 9):
        Untuk plot lahan pertanian dengan luas >= 4.0 Hektar, rangkaian koordinat tertutup
        (Polygon) wajib dilampirkan. Centroid tunggal (titik) hanya diperuntukkan bagi plot < 4.0 Ha.
        """
        if self.area_ha >= 4.0 and not self.geojson_polygon_path:
            raise ValueError(
                f"Kepatuhan Gagal: Plot '{self.plot_id}' memiliki luas {self.area_ha} Ha (>= 4.0 Ha). "
                "Berdasarkan ketentuan Pasal 9 EUDR, berkas poligon spasial GeoJSON (geojson_polygon_path) wajib dilampirkan!"
            )
        return self