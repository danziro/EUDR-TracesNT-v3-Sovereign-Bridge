import os
import json
import asyncio
import traceback
from typing import Optional, Dict, Any
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.database import SessionLocal
from app.logger import log

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")

# Definisi Pipa Topik (Pipeline of Topics)
TOPIC_RAW = "event.raw_ingestion"       # Topik untuk gambar mentah dari WhatsApp
TOPIC_GEO = "event.geo_validation"      # Topik untuk data teks hasil OCR siap audit spasial
TOPIC_DLQ = "event.dlq"                 # Dead-Letter Queue (Karantina pesan error)

producer: Optional[AIOKafkaProducer] = None

async def init_kafka_producer():
    global producer
    for attempt in range(1, 11):
        try:
            producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                max_request_size=52428800
            )
            await producer.start()
            # GANTI print menjadi log.info
            log.info("kafka_producer_connected", status="success", attempt=attempt)
            return
        except Exception as e:
            # GANTI print menjadi log.warning
            log.warning("kafka_producer_connection_failed", attempt=attempt, error=str(e))
            await asyncio.sleep(3)
    
    log.error("kafka_producer_fatal_error", message="Gagal terhubung ke broker setelah 10 percobaan.")
    raise RuntimeError("Gagal terhubung ke broker Kafka.")

async def shutdown_kafka_producer():
    global producer
    if producer:
        await producer.stop()
        print("🔌 [Kafka] Producer dimatikan.")

async def publish_event(topic: str, payload: dict):
    if producer is None:
        raise RuntimeError("Kafka Producer belum siap.")
    await producer.send_and_wait(topic, payload)

async def publish_to_dlq(failed_payload: dict, error_message: str, source_worker: str):
    dlq_payload = {
        "original_payload": failed_payload,
        "error_message": error_message,
        "source_worker": source_worker,
        "failed_at": traceback.format_exc()
    }
    # Logging terstruktur dengan konteks yang jelas
    log.error("dlq_routing_triggered", 
              source_worker=source_worker, 
              plot_id=failed_payload.get("plot_id", "UNKNOWN"),
              error=error_message)
    
    await publish_event(TOPIC_DLQ, dlq_payload)

# ====================================================================
# WORKER 1: VISION & OCR WORKER
# ====================================================================
async def worker_vision_ocr():
    """Worker khusus untuk membaca EXIF dan memproses Computer Vision (OpenCV/EasyOCR)"""
    consumer = AIOKafkaConsumer(
        TOPIC_RAW,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="worker_vision_group",
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        max_partition_fetch_bytes=52428800
    )
    await consumer.start()
    print("👁️ [Worker 1] Vision/OCR Worker mendengarkan foto mentah...")
    
    try:
        from app.services.ingestion import extract_vision_and_exif
        async for msg in consumer:
            payload = msg.value
            try:
                # Proses ekstrak teks dan forensik foto
                extracted_data = await extract_vision_and_exif(payload)
                
                # Lempar hasilnya ke antrean Worker 2
                await publish_event(TOPIC_GEO, extracted_data)
                log.info("worker_1_vision_success", plot_id=payload['plot_id'], next_topic=TOPIC_GEO)
            except Exception as e:
                # Jika foto korup/buram, jangan crash! Lempar ke DLQ
                await publish_to_dlq(payload, str(e), "Worker 1 (Vision)")
    finally:
        await consumer.stop()

# ====================================================================
# WORKER 2: SPATIAL & LEDGER WORKER
# ====================================================================
async def worker_spatial_ledger():
    """Worker khusus untuk komputasi spasial PostGIS dan transaksi ACID Ledger"""
    consumer = AIOKafkaConsumer(
        TOPIC_GEO,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="worker_spatial_group",
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    await consumer.start()
    print("🌍 [Worker 2] Spatial/Ledger Worker bersiap untuk audit PostGIS...")
    
    try:
        from app.services.ingestion import process_spatial_and_ledger
        async for msg in consumer:
            payload = msg.value
            try:
                # Buka koneksi database HANYA pada saat kueri spasial dibutuhkan
                async with SessionLocal() as db:
                    await process_spatial_and_ledger(payload, db)
                log.info("worker_2_spatial_success", plot_id=payload['plot_id'], status="COMPLIANT_SAVED")
            except Exception as e:
                # Jika kuota tidak cukup atau ditolak hutan lindung, lempar ke DLQ
                await publish_to_dlq(payload, str(e), "Worker 2 (Spatial)")
    finally:
        await consumer.stop()

async def start_kafka_consumer():
    """Fungsi orkestrator untuk menjalankan semua worker secara paralel"""
    await asyncio.gather(
        worker_vision_ocr(),
        worker_spatial_ledger()
    )