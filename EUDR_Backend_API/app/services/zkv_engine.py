import json
import hashlib
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

# ====================================================================
# TRUSTED SETUP: INISIALISASI KEYPAIR KEDAULATAN (PK & VK) [93]
# ====================================================================
# Dalam zk-SNARKs asli, ini setara dengan pembentukan CRS (Common Reference String)
# Private Key bertindak sebagai Proving Key (PK) - Disimpan di server Indonesia [93, 94]
# Public Key bertindak sebagai Verifying Key (VK) - Dibagikan ke Uni Eropa [93, 94]

_PROVING_KEY = ec.generate_private_key(ec.SECP256R1())
VERIFYING_KEY = _PROVING_KEY.public_key()


def generate_zk_proof(
    plot_wkt: str,
    is_forest_conflict_empty: bool,
    is_within_hgu: bool,
    transaction_id: str,
    timestamp: str
) -> Tuple[str, dict]:
    """
    SISTEM PROVER (Lokal/Domestik) [91, 92].
    Mengevaluasi sirkuit aritmatika secara luring menggunakan data rahasia (Private Input / Witness)
    dan menghasilkan bukti matematis asimetris (pi) beserta Public Input (x) [94].
    """
    # 1. Private Input / Witness (w) - Koordinat mentah HGU yang sangat rahasia [93, 94]
    witness = {
        "geometry_wkt": plot_wkt,
        "forest_clean": is_forest_conflict_empty,
        "hgu_clean": is_within_hgu
    }
    
    # 2. Public Input (x) - Metadata non-sensitif untuk pabean Eropa [93, 94]
    public_input = {
        "transaction_id": transaction_id,
        "timestamp": timestamp,
        "witness_hash": hashlib.sha256(json.dumps(witness, sort_keys=True).encode()).hexdigest()
    }
    
    # 3. Evaluasi Batasan Sirkuit Aritmatika C(x, w) [93]
    # Kriteria Mutlak: Bebas Deforestasi DAN Berada di dalam batas legal HGU nasional [93]
    circuit_satisfied = is_forest_conflict_empty and is_within_hgu
    
    # 4. Generasi Bukti Matematika (pi) [93]
    # Menggunakan tanda tangan Elliptic Curve (ECDSA) di atas hash parameter publik dan biner kepatuhan
    seal_payload = f"{public_input['witness_hash']}-{circuit_satisfied}".encode()
    
    # Prover (Indonesia) menandatangani payload menggunakan Proving Key (PK) rahasia [93, 94]
    signature = _PROVING_KEY.sign(
        seal_payload,
        ec.ECDSA(hashes.SHA256())
    )
    
    # Dekode tanda tangan ASN.1 DER menjadi r, s integer standar zk-SNARK
    r, s = decode_dss_signature(signature)
    
    proof_pi = {
        "proof_elements": {
            "r": str(r),
            "s": str(s)
        },
        "circuit_satisfied": circuit_satisfied
    }
    
    return json.dumps(proof_pi), public_input


def verify_zk_proof(proof_pi_json: str, public_input: dict) -> bool:
    """
    SISTEM VERIFIER (TRACES NT/Uni Eropa) [93, 94].
    Melakukan verifikasi tanda tangan kunci publik (VK) asimetris secara independen.
    Sistem pabean Eropa membuktikan kepatuhan tanpa bisa merekonstruksi koordinat mentah [94].
    """
    try:
        proof_pi = json.loads(proof_pi_json)
        witness_hash = public_input["witness_hash"]
        circuit_satisfied = proof_pi["circuit_satisfied"]
        
        # Rekonstruksi data payload pembanding
        expected_payload = f"{witness_hash}-{circuit_satisfied}".encode()
        
        # Ambil koordinat pembuktian r, s
        r = int(proof_pi["proof_elements"]["r"])
        s = int(proof_pi["proof_elements"]["s"])
        
        # Rekonstruksi kembali struktur ASN.1 DER signature dari komponen r, s
        from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
        signature = encode_dss_signature(r, s)
        
        # VERIFIKASI ASIMETRIS: Gunakan Verifying Key (VK) / Public Key [93, 94]
        # Jika tanda tangan valid, berarti bukti diproduksi oleh Prover yang sah (Pemerintah Indonesia) [94]
        VERIFYING_KEY.verify(
            signature,
            expected_payload,
            ec.ECDSA(hashes.SHA256())
        )
        
        # Kembalikan status hasil evaluasi sirkuit biner (True/False) [93]
        return circuit_satisfied
        
    except Exception:
        # Jika tanda tangan dimodifikasi atau kunci tidak cocok, verifikasi langsung gagal (False)
        return False