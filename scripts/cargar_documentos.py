# scripts/cargar_documentos.py
from db_config import get_mongo_client
from models import Usuario, Producto
from bson import ObjectId

def cargar_documentos_de_ejemplo():
    db = get_mongo_client()  # por defecto mongodb://localhost:27017/mi_ecommerce

    # Colecciones
    usuarios_coll = db["usuarios"]
    productos_coll = db["productos"]

    # Crear ejemplos de usuarios
    usuario1 = Usuario(nombre="Alice", email="alice@example.com", categoria="TOP")
    usuario2 = Usuario(nombre="Bob", email="bob@example.com", categoria="MEDIUM")

    # Insertar usuarios en MongoDB
    usuarios_coll.insert_one(usuario1.__dict__)
    usuarios_coll.insert_one(usuario2.__dict__)

    # Crear ejemplos de productos
    producto1 = Producto(nombre="Laptop Gamer", descripcion="Laptop muy potente", precio=1500.99, stock=10)
    producto2 = Producto(nombre="Smartphone X", descripcion="Gama alta", precio=999.99, stock=5)

    # Insertar productos en MongoDB
    productos_coll.insert_one(producto1.__dict__)
    productos_coll.insert_one(producto2.__dict__)

    print("Documentos de ejemplo cargados con éxito.")

if __name__ == "__main__":
    cargar_documentos_de_ejemplo()
