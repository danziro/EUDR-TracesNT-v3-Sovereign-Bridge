import os
from typing import Dict, Any, List

class TRACESM2MCompiler:
    """
    Kompilator Payload M2M TRACES NT Uni Eropa berbasis skema JSON-LD [39].
    """
    def __init__(self, operator_eori: str = "ID-EORI-2026-INHU-CORP"):
        self.operator_eori = operator_eori

    def compile_due_diligence_statement(
        self,
        plot_id: str,
        commodity_hs_code: str,
        scientific_name: str,
        net_weight_kg: float,
        clean_geometry_wkt: str,
        g2g_token: str,
        zk_proof_pi: str,
        zk_public_input: dict
    ) -> Dict[str, Any]:
        """
        Menyusun berkas payload terstruktur JSON-LD untuk pengajuan 
        Due Diligence Statement (DDS) otomatis tanpa intervensi manual [39].
        """
        # Konversi WKT Geometri Bersih menjadi Array Koordinat Spasial GeoJSON (WGS84) [41]
        # PENTING: TRACES NT mewajibkan proyeksi geografis WGS84 (EPSG:4326) [41]
        from shapely.wkt import loads
        geom_shape = loads(clean_geometry_wkt)
        
        # Ekstraksi array koordinat luar (exterior ring)
        coordinates_array = list(geom_shape.exterior.coords)

        # 1. Konstruksi Dokumen Semantik JSON-LD [39, 40]
        json_ld_payload = {
            "@context": {
                "eudr": "https://gateway.traces.ec.europa.eu/schema/eudr/v1/context.jsonld",
                "xsd": "http://www.w3.org/2001/XMLSchema#"
            },
            "@type": "eudr:DueDiligenceStatement",
            
            # PILAR I: OPERATOR PROFILE (EORI Resmi Importir/Eksportir) [40]
            "eudr:operator": {
                "@type": "eudr:EconomicOperator",
                "eudr:eoriNumber": self.operator_eori,
                "eudr:countryOfOrigin": "ID"
            },
            
            # PILAR II: PRODUCT PROFILE (Spesifikasi Fisik Komoditas) [41]
            "eudr:product": {
                "@type": "eudr:CommodityDetails",
                "eudr:hsCode": commodity_hs_code, # Contoh: '151110' untuk Crude Palm Oil (CPO)
                "eudr:scientificName": scientific_name, # Contoh: 'Elaeis guineensis'
                "eudr:netWeightKilograms": {
                    "@value": round(net_weight_kg, 2),
                    "@type": "xsd:decimal"
                }
            },
            
            # PILAR III: GEOSPATIAL ARRAY (Batas Poligon Hasil Sanitasi & Auto-Clipping) [41]
            "eudr:geospatialVerification": {
                "@type": "eudr:GeospatialArray",
                "eudr:spatialReferenceSystem": "EPSG:4326",
                "eudr:geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates_array]
                }
            },
            
            # PILAR IV: SOVEREIGN TRACEABILITY LINKS (ZKV & G2G National Clearance Token) [41, 95]
            "eudr:traceabilityLinks": {
                "@type": "eudr:CryptographicChain",
                "eudr:nationalG2GToken": g2g_token,
                "eudr:zeroKnowledgeVerification": {
                    "proof_pi": zk_proof_pi,
                    "public_input_x": zk_public_input
                }
            }
        }
        
        return json_ld_payload