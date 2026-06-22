import uuid
import json
from datetime import datetime
from fastapi import HTTPException
from app.services.zkv_engine import verify_zk_proof
from app.logger import log  # <-- Pastikan logger terimpor

class G2GGateway:
    """
    Sistem Gerbang Integrasi G2G Tiga-Arah (Three-Way Handshake)
    didukung oleh Sirkuit ZK-SNARKs Asimetris [95, 96].
    """
    def __init__(self):
        self.national_ledger_path = "/app/national_g2g_ledger.jsonl"

    async def submit_to_national_dashboard(self, proof_pi: str, public_input: dict) -> str:
        """
        Arah Kedua: Verifikasi Bukti di tingkat Dasbor Nasional Indonesia [96].
        Jika terbukti patuh, dasbor menandatangani persetujuan dan merilis Token G2G Berdaulat [96].
        """
        # Verifikasi bukti ZK secara lokal menggunakan public key nasional
        is_valid = verify_zk_proof(proof_pi, public_input)
        
        if not is_valid:
            log.error("national_dashboard_zk_rejected", 
                      transaction_id=public_input["transaction_id"],
                      reason="Data spasial melanggar tumpang tindih kawasan hutan.")
            raise HTTPException(
                status_code=400,
                detail="Dasbor Nasional menolak bukti: Koordinat terdeteksi melanggar batas hutan lindung."
            )
            
        domestic_token = f"TOKEN_G2G_ID_{uuid.uuid4().hex[:12].upper()}_{datetime.now().year}"
        
        # Catat ke buku besar rahasia nasional untuk kebutuhan audit internal negara [96]
        try:
            with open(self.national_ledger_path, "a") as f:
                f.write(json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "transaction_id": public_input["transaction_id"],
                    "issued_token": domestic_token,
                    "status": "APPROVED"
                }) + "\n")
        except Exception as e:
            log.warning("national_ledger_write_failed", error=str(e))
            
        log.info("national_dashboard_zk_cleared", 
                 transaction_id=public_input["transaction_id"], 
                 g2g_token=domestic_token)
                 
        return domestic_token

    async def transmit_to_traces_nt(self, proof_pi: str, public_input: dict, domestic_token: str) -> dict:
        """
        Arah Ketiga: Verifikator Uni Eropa di TRACES NT Brusel melakukan pengecekan bukti ZK [97].
        Uni Eropa memvalidasi matematika bukti tanpa pernah bisa melacak koordinat spasial HGU asli [94, 97].
        """
        eu_verification = verify_zk_proof(proof_pi, public_input)
        
        if not eu_verification or not domestic_token.startswith("TOKEN_G2G_ID_"):
            log.error("traces_nt_handshake_failed", 
                      transaction_id=public_input["transaction_id"],
                      reason="Bukti kriptografi palsu atau token domestik ilegal.")
            return {
                "status_code": 401,
                "submission_status": "REJECTED",
                "server_errors": ["Invalid Cryptographic Proof", "Domestic G2G Token Validation Failed"]
            }
            
        official_urn = f"URN:EUDR:TRACES:ZKV:ID:{uuid.uuid4().hex[:16].upper()}"
        
        log.info("traces_nt_urn_issued", 
                 transaction_id=public_input["transaction_id"], 
                 urn=official_urn)
                 
        return {
            "status_code": 201,
            "urn_reference": official_urn,
            "submission_status": "ACCEPTED",
            "timestamp": datetime.now().isoformat(),
            "environment": "PRODUCTION_ZKV_GATEWAY",
            "validation_metadata": {
                "g2g_token_applied": domestic_token,
                "zk_circuit_status": "VERIFIED_COMPLIANT_NO_RAW_GEOMETRY_EXPOSED"
            }
        }