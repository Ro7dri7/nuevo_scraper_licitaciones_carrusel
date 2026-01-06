# 1. Usamos la imagen oficial de Playwright que ya tiene Python y los navegadores instalados
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# 2. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiamos el archivo de dependencias
COPY requirements.txt .

# 4. Instalamos las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos todo el contenido de tu proyecto al contenedor
COPY . .

# 6. Comando para ejecutar la API con Uvicorn
# NOTA: Usamos "main:app" (módulo:variable), NO "main.py:app"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]