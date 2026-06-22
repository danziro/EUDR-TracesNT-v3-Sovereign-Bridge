import os
import hashlib
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import SecurePersonalDataVault
from app.logger import log

# Ambil kunci enkripsi vault dari env (atau gunakan key dummy untuk sandbox)
VAULT_KEY = os.getenv("VAULT_SECRET_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(VAULT_KEY.encode())


def generate_association_token(farmer_name: str, nib: str) -> str:
    """Menghasilkan hash token searah (SHA-256) sebagai kunci penghubung anonim"""
    raw_string = f"{farmer_name}-{nib}"
    return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()


async def encrypt_and_vault_pii(
    farmer_name: str, 
    nib: str, 
    db: AsyncSession
) -> str:
    """
    Enkripsi data pribadi petani menggunakan AES-256 
    dan simpan ke dalam Secure Vault. Mengembalikan Token Asosiasi [89].
    """
    token = generate_association_token(farmer_name, nib)
    
    # Periksa apakah token ini sudah terdaftar di vault (mencegah duplikasi data)
    query = select(SecurePersonalDataVault).filter(SecurePersonalDataVault.association_token == token)
    result = await db.execute(query)
    existing_entry = result.scalar_one_or_none()
    
    if existing_entry:
        return token
        
    # Proses Enkripsi data pribadi [89]
    encrypted_name = cipher_suite.encrypt(farmer_name.encode('utf-8')).decode('utf-8')
    encrypted_nib = cipher_suite.encrypt(nib.encode('utf-8')).decode('utf-8')
    
    vault_entry = SecurePersonalDataVault(
        association_token=token,
        encrypted_farmer_name=encrypted_name,
        encrypted_nib=encrypted_nib
    )
    db.add(vault_entry)
    # db.commit() akan ditangani oleh transaction block utama di hulu
    
    log.info("pii_vaulted_successfully", association_token=token)
    return token


async def decrypt_pii_from_vault(
    association_token: str, 
    db: AsyncSession
) -> dict:
    """
    Mengambil data dari Vault dan mendekripsinya kembali menjadi plaintext.
    Jika data sudah dihapus (GDPR Right to Be Forgotten), kembalikan data anonim [89].
    """
    query = select(SecurePersonalDataVault).filter(SecurePersonalDataVault.association_token == association_token)
    result = await db.execute(query)
    entry = result.scalar_one_or_none()
    
    if not entry:
        # Menandakan data pribadi telah dihapus atas permintaan GDPR [89]
        log.warning("pii_not_found_or_forgotten_by_gdpr", token=association_token)
        return {
            "farmer_name": "ANONYMOUS_REMOVED_BY_GDPR_REQUEST",
            "nib": "DELETED_GDPR"
        }
        
    try:
        decrypted_name = cipher_suite.decrypt(entry.encrypted_farmer_name.encode('utf-8')).decode('utf-8')
        decrypted_nib = cipher_suite.decrypt(entry.encrypted_nib.encode('utf-8')).decode('utf-8')
        return {
            "farmer_name": decrypted_name,
            "nib": decrypted_nib
        }
    except Exception as e:
        log.error("vault_decryption_failed", token=association_token, error=str(e))
        return {
            "farmer_name": "DECRYPTION_ERROR_SECURE",
            "nib": "ERROR"
        }