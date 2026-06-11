# ====================================================================
# PROJECT   : Sovereign RegTech Protocol (EUDR Gateway SDK)
# MODULE    : soap_wrapper.py
# STANDARD  : SOAP SOAP-XML v3.0 Protocol (TRACES NT European Gateway)
# SECURITY  : WS-Security (WSS) & XML Namespace Compiling
# ====================================================================

from typing import Dict, Any
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

class TRACESNTSoapV3Compiler:
    """
    Kompilator Skema REST-to-SOAP XML v3.0 untuk TRACES NT.
    Menerjemahkan payload JSON-LD modern menjadi envelope SOAP XML terstruktur
    lengkap dengan penanganan WS-Security dan pembungkus namespace.
    """

    def __init__(self, username: str = "ID_SOVEREIGN_GATEWAY", wss_token: str = "MOCK_WSS_SECURE_TOKEN"):
        self.username = username
        self.wss_token = wss_token

    def compile_soap_envelope(self, json_ld_payload: Dict[str, Any]) -> str:
        """
        Menyusun Envelope SOAP v3 secara berjenjang dari data semantik JSON-LD.
        Mengunci standardisasi XML secara string-template untuk menjaga presisi
        wsse:Security dan namespace agar tidak tergeser oleh default parser python.
        """
        metadata = json_ld_payload.get("metadata", {})
        commodity = json_ld_payload.get("commodity_details", {})
        geospatial = json_ld_payload.get("geospatial_verification", {})
        legality = json_ld_payload.get("legality_documentation", {})
        verdict = json_ld_payload.get("due_diligence_verdict", {})

        # Parsing Koordinat Geometri Spasial (WGS84)
        geometry_xml_nodes = ""
        if "polygon_geometry" in geospatial:
            coords = geospatial["polygon_geometry"].get("coordinates", [[]])[0]
            coords_str = " ".join([f"{lon},{lat}" for lon, lat in coords])
            geometry_xml_nodes = f"""<v3:geometryType>Polygon</v3:geometryType>
                        <v3:coordinates>{coords_str}</v3:coordinates>"""
        elif "centroid" in geospatial:
            lat = geospatial["centroid"].get("latitude")
            lon = geospatial["centroid"].get("longitude")
            geometry_xml_nodes = f"""<v3:geometryType>Point</v3:geometryType>
                        <v3:coordinates>{lon},{lat}</v3:coordinates>"""

        # Pembentukan Dokumen XML SOAP Envelope V3
        soap_envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:v3="https://gateway.traces.ec.europa.eu/schema/eudr/v3/service"
                  xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
                  xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
   <soapenv:Header>
      <!-- WS-Security Header (Oasis Standard) -->
      <wsse:Security>
         <wsse:UsernameToken wsu:Id="UsernameToken-1">
            <wsse:Username>{self.username}</wsse:Username>
            <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{self.wss_token}</wsse:Password>
         </wsse:UsernameToken>
      </wsse:Security>
   </soapenv:Header>
   <soapenv:Body>
      <v3:SubmitDueDiligenceStatementRequest>
         <v3:DdsId>{json_ld_payload.get("dds_id")}</v3:DdsId>
         
         <!-- Operator Profile (EORI) -->
         <v3:OperatorDetails>
            <v3:EoriNumber>{metadata.get("operator_eori")}</v3:EoriNumber>
            <v3:CompanyName>{metadata.get("operator_name")}</v3:CompanyName>
            <v3:CountryCode>{metadata.get("origin_country")}</v3:CountryCode>
         </v3:OperatorDetails>
         
         <!-- Commodity & Volume Profile -->
         <v3:CommodityDetails>
            <v3:HsCode>{commodity.get("hs_code")}</v3:HsCode>
            <v3:ScientificName>{commodity.get("name")}</v3:ScientificName>
            <v3:NetWeightKilograms>{int(commodity.get("weight_estimate_mt", 0) * 1000)}</v3:NetWeightKilograms>
            <v3:AnnualCeilingQuantityKilograms>{int(commodity.get("annual_quantity_estimate_mt", 0) * 1000)}</v3:AnnualCeilingQuantityKilograms>
         </v3:CommodityDetails>
         
         <!-- Geospatial Verification Block (Centroid vs Polygon) -->
         <v3:GeospatialExtent>
            <v3:PlotId>{geospatial.get("plot_id")}</v3:PlotId>
            <v3:AreaHectares>{geospatial.get("area_ha")}</v3:AreaHectares>
            <v3:ReferenceSystem>{geospatial.get("crs")}</v3:ReferenceSystem>
            <v3:SpatialBoundary>
                {geometry_xml_nodes}
            </v3:SpatialBoundary>
         </v3:GeospatialExtent>

         <!-- Legality & ISPO Attestation Block -->
         <v3:LegalityAttestation>
            <v3:BusinessLicenseNib>{legality.get("business_license_nib")}</v3:BusinessLicenseNib>
            <v3:LandPermitHgu>{legality.get("land_permit_hgu")}</v3:LandPermitHgu>
            <v3:IspoCertificateNumber>{legality.get("ispo_certification", {}).get("certificate_number")}</v3:IspoCertificateNumber>
            <v3:EnvironmentalPermit>{legality.get("environmental_permit_type")}:{legality.get("environmental_permit_number")}</v3:EnvironmentalPermit>
            <v3:FpicStatus>{legality.get("fpic_status")}</v3:FpicStatus>
         </v3:LegalityAttestation>

         <!-- Risk & Cryptographic Assesment -->
         <v3:AuditAssessment>
            <v3:RiskVerdict>{verdict.get("status")}</v3:RiskVerdict>
            <v3:AggregateRiskScore>{verdict.get("aggregate_risk_score")}</v3:AggregateRiskScore>
            <v3:DigitalSignatureVerification>{verdict.get("ai_audit_hash")}</v3:DigitalSignatureVerification>
            <v3:ComplianceTimestamp>{datetime.now(timezone.utc).isoformat()}</v3:ComplianceTimestamp>
         </v3:AuditAssessment>
      </v3:SubmitDueDiligenceStatementRequest>
   </soapenv:Body>
</soapenv:Envelope>"""
        return soap_envelope