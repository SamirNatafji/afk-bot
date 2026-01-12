FROM python:3.12-slim

# تثبيت FFmpeg والمكتبات الأساسية
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus0 \
    libsodium23 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ ملفات المشروع
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# تشغيل البوت
CMD ["python", "main.py"]
