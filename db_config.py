# db_config.py
import os
from pymongo import MongoClient

def get_mongo_client():
    # Leer variables de entorno que definen la URI
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/mi_ecommerce")
    client = MongoClient(mongo_uri)
    # Extraer el nombre de la BD de la URI o usar por defecto
    db_name = mongo_uri.rsplit('/', 1)[-1]  # "mi_ecommerce" si la URI tiene forma "mongodb://.../mi_ecommerce"
    db = client[db_name]
    return db
