from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class FarmerPlotInput(BaseModel):
    plot_id: str = Field(..., example="PLOT-INHU-001")
    nib: str = Field(..., example="123456789")
    commodity: str = "Oil Palm"
    latitude: float
    longitude: float
    area_ha: float
    farmer_name: str
    annual_quantity_estimate_mt: float = Field(..., example=50.0)

    @field_validator('latitude')
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not (-90 <= v <= 90):
            raise ValueError("Latitude harus berada di antara -90 dan 90")
        if v == 0:
            raise ValueError("Koordinat tidak boleh presisi nol")
        return v

    @field_validator('longitude')
    @classmethod
    def validate_lon(cls, v: float) -> float:
        if not (-180 <= v <= 180):
            raise ValueError("Longitude harus berada di antara -180 dan 180")
        if v == 0:
            raise ValueError("Koordinat tidak boleh presisi nol")
        return v
