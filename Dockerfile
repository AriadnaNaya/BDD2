# Dockerfile
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de archivos de la aplicación
COPY . /app

# Exponer el puerto donde correrá la app (Flask usa 5000 por defecto)
EXPOSE 5000

# Variable de entorno opcional (puedes usarla para producción)
ENV FLASK_ENV=production

# Comando para iniciar la aplicación
CMD ["python", "app.py"]
