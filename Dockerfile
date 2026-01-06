# 1. Usamos una imagen base ligera de Python
FROM python:3.11-slim-bookworm

# 2. Establecemos variables de entorno para evitar archivos temporales y asegurar la salida de logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 3. Instalamos dependencias básicas del sistema necesarias para descargar navegadores
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 4. Copiamos e instalamos las librerías de Python primero
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. INSTALACIÓN CRÍTICA: Descargamos el navegador y las dependencias de sistema de Playwright
# Esto instala Chromium y todas las librerías de Linux que necesita para correr en la nube
RUN playwright install chromium
RUN playwright install-deps chromium

# 6. Copiamos el resto del código
COPY . .

# 7. Exponemos el puerto y lanzamos la app
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]