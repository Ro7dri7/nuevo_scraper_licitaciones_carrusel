# Usamos la imagen oficial de Playwright que ya tiene Python y navegadores
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Comando para ejecutar la API
CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "10000"]