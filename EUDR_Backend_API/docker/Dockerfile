# Menggunakan image Python resmi yang ringan
FROM python:3.11-slim

# Set direktori kerja di dalam container
WORKDIR /app

# Instalasi dependency sistem operasi untuk OpenCV, GDAL, dan PostgreSQL
# 'libgl1-mesa-glx' diganti dengan 'libgl1' untuk kompatibilitas Debian terbaru (Trixie)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Salin daftar pustaka Python dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode proyek kita ke dalam container
COPY . .

# Jalankan server FastAPI menggunakan Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]