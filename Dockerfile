# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5000
ENV FLASK_ENV=production

# Agregar la línea que pone /app en el PYTHONPATH
ENV PYTHONPATH=/app

CMD ["bash", "-c", "python scripts/cargar_documentos.py && python app.py"]
