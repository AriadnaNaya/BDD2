# BDD2

# README

Este documento explica de manera sencilla cómo levantar y probar una aplicación desarrollada en **Flask** que utiliza **MongoDB** y **Redis**, todo orquestado con **Docker Compose**. Está pensado para alguien que no tenga experiencia previa con Docker.

---

## 1. Requisitos previos

1. **Docker Desktop** instalado en tu equipo.  
   - Puedes descargarlo desde [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop).  
   - Asegúrate de que Docker Desktop se esté ejecutando (el ícono de Docker aparece en la barra de tareas).

2. **Docker Compose**:  
   - Viene incluido con Docker Desktop a partir de versiones recientes, así que no necesitas instalarlo por separado.

---

## 2. Estructura de archivos

En la carpeta raíz del proyecto (por ejemplo, `mi_proyecto`), deberías contar con los siguientes archivos:

```
mi_proyecto
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── (otros archivos si tu app los necesita)
```

- **app.py**: Código principal de la aplicación Flask.  
- **requirements.txt**: Dependencias de Python (Flask, pymongo, redis, etc.).  
- **Dockerfile**: Instrucciones para construir la imagen de la aplicación.  
- **docker-compose.yml**: Archivo que orquesta la aplicación Flask junto con MongoDB y Redis.

---

## 3. Explicación de los archivos clave

### 3.1 Dockerfile

Ejemplo resumido:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python", "app.py"]
```
- **FROM python:3.9-slim**: Parte de una imagen base de Python.  
- **WORKDIR /app**: Establece el directorio de trabajo dentro del contenedor.  
- **COPY requirements.txt .** y **RUN pip install...**: Instala las dependencias.  
- **COPY . /app**: Copia el código fuente al contenedor.  
- **EXPOSE 5000**: Expone el puerto 5000.  
- **CMD ["python", "app.py"]**: Indica cómo se inicia la aplicación dentro del contenedor.

### 3.2 docker-compose.yml

Ejemplo resumido:
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    container_name: mi_ecommerce_mongo
    ports:
      - "27017:27017"

  redis:
    image: redis:latest
    container_name: mi_ecommerce_redis
    ports:
      - "6379:6379"

  app:
    build: .
    container_name: mi_ecommerce_app
    ports:
      - "5000:5000"
    environment:
      # Variables de entorno que el app.py utilizará
      MONGO_URI: mongodb://mongodb:27017/mi_ecommerce
      REDIS_HOST: redis
      REDIS_PORT: 6379
    depends_on:
      - mongodb
      - redis
```

- **services**: Define varios contenedores (mongodb, redis, app).  
- **mongodb** y **redis**: Usa imágenes oficiales de MongoDB y Redis.  
- **app**: Construye la imagen usando el Dockerfile local (la directiva `build: .` apunta a tu carpeta actual).  
- **ports**: Abre los puertos en tu máquina (host) para poder acceder a los servicios.  
- **environment**: Variables de entorno que tu aplicación Flask leerá para conectarse a MongoDB y Redis.  
- **depends_on**: Asegura que MongoDB y Redis se inicien antes que tu app.

---

## 4. Pasos para ejecutar la aplicación

1. **Abrir una terminal o consola**  
   - Puede ser la de **Windows**, **macOS** o **Linux** (según tu sistema operativo).  
   - Dirígete a la carpeta donde se encuentra tu proyecto (donde está `docker-compose.yml`).

2. **Levantar los contenedores con Docker Compose**  
   ```bash
   docker-compose up --build
   ```
   - La opción `--build` fuerza a Docker a reconstruir la imagen de la aplicación, garantizando que se apliquen los cambios recientes.  
   - Verás que Docker descarga (si no los tienes) las imágenes de `mongo` y `redis`, luego construye tu imagen de la app Flask y, finalmente, arranca los tres contenedores.  

3. **Ver los logs**  
   - En la misma ventana aparecerán los logs de MongoDB, Redis y la aplicación Flask.  
   - Si todo va bien, tu aplicación Flask mostrará algo como:  
     ```
     Running on http://0.0.0.0:5000
     ```

4. **Acceder a la aplicación**  
   - Abre tu navegador e ingresa a [http://localhost:5000](http://localhost:5000).  
   - Deberías ver la página o el mensaje que tu `app.py` haya definido en su ruta principal.

5. **Modo “detached”** (opcional)  
   - Si no quieres ver los logs en la consola y prefieres que todo se ejecute en segundo plano, usa:  
     ```bash
     docker-compose up --build -d
     ```
   - Para ver los logs en segundo plano, podrías luego ejecutar:  
     ```bash
     docker-compose logs -f
     ```

6. **Detener la aplicación**  
   - Ve a la terminal donde está corriendo y presiona `Ctrl + C`.  
   - Si corriste en modo detached, simplemente ejecuta:  
     ```bash
     docker-compose down
     ```
   - Esto detiene y elimina los contenedores (no elimina imágenes ni datos persistentes en volúmenes, salvo que se configure lo contrario).

---

## 5. Cómo probar la aplicación (Requests a la API)

Si tu aplicación Flask provee endpoints, puedes hacer pruebas con:

1. **Navegador**  
   - Simplemente visitas [http://localhost:5000](http://localhost:5000) (o el endpoint que corresponda).

2. **cURL** (en la terminal)  
   - Ejemplo:  
     ```bash
     curl http://localhost:5000/productos
     ```
   - Devuelve un JSON con la lista de productos (suponiendo que tengas un endpoint GET /productos).

3. **Herramientas como Postman o Insomnia**  
   - Puedes configurar llamadas HTTP a tus endpoints (GET, POST, PUT, DELETE) para ver respuestas JSON y añadir cuerpos de petición.

---

## 6. Preguntas frecuentes

**1. ¿Por qué se muestra un warning diciendo que “This is a development server”?**  
   - Flask, por defecto, corre en modo desarrollo. No pasa nada, es solo un aviso. Para producción se recomienda usar un servidor WSGI como `gunicorn` o `uwsgi`. Pero para este ejemplo educativo no es estrictamente necesario.

**2. ¿Y si me sale el error “page not found” o “ERR_EMPTY_RESPONSE” al acceder a http://localhost:5000?**  
   - Asegúrate de que:
     1. Flask escuche en `0.0.0.0` dentro del contenedor (`app.run(host="0.0.0.0", port=5000)`).  
     2. Tu `docker-compose.yml` mapée el puerto `5000:5000`.  
     3. Estás visitando la URL `http://localhost:5000` (sin errores tipográficos).

**3. ¿Cómo entro a la base de datos MongoDB para ver si se insertan datos?**  
   - Con Docker Compose, MongoDB está mapeado por defecto en el puerto 27017.  
   - Instala un cliente de MongoDB (por ejemplo, MongoDB Compass) y conéctate a `mongodb://localhost:27017`.  
   - Ahí verás la base de datos creada por tu aplicación (p.ej. `mi_ecommerce`).

**4. ¿Cómo verifico Redis?**  
   - Redis corre en el puerto 6379.  
   - Puedes usar la consola de Redis:  
     ```bash
     redis-cli -h 127.0.0.1 -p 6379
     ```
   - Y ejecutar comandos para ver, por ejemplo, claves almacenadas (`KEYS *`) u otras operaciones.

---

## 7. Resumen

1. **Instala Docker Desktop** y asegúrate de que esté en ejecución.  
2. **Clona** o copia este proyecto a tu máquina.  
3. **Desde la carpeta del proyecto**, corre `docker-compose up --build`.

MongoDB (NoSQL documental): Para almacenar de forma persistente las entidades principales de la aplicación (usuarios, productos, pedidos, etc.).
Redis (clave-valor en memoria): Para manejar datos temporales como la sesión de usuario y el carrito de compras antes de su confirmación.
