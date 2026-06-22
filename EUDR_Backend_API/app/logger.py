import logging
import structlog

def setup_logger():
    """
    Mengonfigurasi Structured JSON Logging.
    Mengubah output log teks biasa menjadi format JSON kaya metadata.
    """
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,           # Menambahkan "level": "info/error"
            structlog.stdlib.add_logger_name,         # Nama modul yang mengeksekusi
            structlog.processors.TimeStamper(fmt="iso"), # Menambahkan "timestamp" UTC
            structlog.processors.StackInfoRenderer(), # Menangkap stack trace jika terjadi crash
            structlog.processors.format_exc_info,     # Memformat exception error
            structlog.processors.JSONRenderer()       # Output akhir diubah menjadi JSON
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set level log bawaan Python
    logging.basicConfig(level=logging.INFO)
    
    return structlog.get_logger("geoai_eudr")

# Instansiasi objek logger global yang bisa dipanggil dari mana saja
log = setup_logger()