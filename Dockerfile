# Gunakan Python versi 3.11 yang ringan sebagai dasar
FROM python:3.11-slim

# Atur environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Atur direktori kerja di dalam container
WORKDIR /app

# Salin file daftar dependensi
COPY requirements.txt .

# Install dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file proyek ke dalam container
COPY . .

# Jalankan collectstatic untuk mengumpulkan file statis
RUN python manage.py collectstatic --no-input

# Buka port 8000 di dalam container
EXPOSE 8000
