# app.py
from flask import Flask, session, request, redirect, url_for, render_template, jsonify
from db_config import get_mongo_client
from redis_config import get_redis_client
from bson import ObjectId
import uuid
import json

app = Flask(__name__)
app.secret_key = "SECRET_KEY_DE_EJEMPLO"  # Cambiar por algo seguro en producción

# Conexiones a las BD
db = get_mongo_client()
redis_client = get_redis_client()

@app.before_request
def asegurar_sesion():
    """
    Middleware para asegurarnos de que cada usuario tenga un identificador único de sesión.
    Podríamos guardar en Redis el estado de la sesión.
    """
    if 'user_session_id' not in session:
        # Genera un ID de sesión único y lo guarda en la cookie de sesión
        session['user_session_id'] = str(uuid.uuid4())

@app.route("/")
def index():
    return "Bienvenido a la plataforma de comercio electrónico."

@app.route("/login", methods=["POST"])
def login():
    """
    Login de usuario muy simplificado.
    Asume que recibe 'email' por POST y, si existe en MongoDB, se inicia la sesión.
    """
    email = request.form.get("email")
    usuarios_coll = db["usuarios"]
    usuario = usuarios_coll.find_one({"email": email})

    if usuario:
        # Guardar la información del usuario en Redis usando user_session_id como key
        session_id = session['user_session_id']
        redis_client.hset(f"session:{session_id}", "user_id", str(usuario["_id"]))
        redis_client.hset(f"session:{session_id}", "user_email", usuario["email"])
        return jsonify({"message": "Usuario logueado correctamente", "user": usuario["email"]})
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404

@app.route("/logout", methods=["GET"])
def logout():
    """
    Cerrar sesión: limpiamos en Redis la key asociada al session_id.
    """
    session_id = session['user_session_id']
    redis_client.delete(f"session:{session_id}")
    session.pop('user_session_id', None)
    return redirect(url_for('index'))

@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    """
    Agrega un producto al carrito en Redis.
    Espera: product_id, cantidad
    """
    session_id = session['user_session_id']
    product_id = request.form.get("product_id")
    cantidad = int(request.form.get("cantidad", 1))

    # La clave del carrito se compone de "cart:{session_id}"
    cart_key = f"cart:{session_id}"

    # Si el producto ya existe, sumamos cantidades
    existing_qty = redis_client.hget(cart_key, product_id)
    if existing_qty is not None:
        cantidad += int(existing_qty)

    redis_client.hset(cart_key, product_id, cantidad)
    return jsonify({"message": "Producto agregado al carrito", "product_id": product_id, "cantidad": cantidad})

@app.route("/ver_carrito", methods=["GET"])
def ver_carrito():
    """
    Muestra los productos en el carrito consultando Redis.
    """
    session_id = session['user_session_id']
    cart_key = f"cart:{session_id}"
    cart_items = redis_client.hgetall(cart_key)

    # Convertir keys/values de binario a strings
    resultado = {}
    for k, v in cart_items.items():
        resultado[k.decode("utf-8")] = int(v.decode("utf-8"))

    return jsonify({"carrito": resultado})

@app.route("/confirmar_pedido", methods=["POST"])
def confirmar_pedido():
    """
    Convierte el carrito en un pedido en MongoDB.
    """
    session_id = session['user_session_id']
    cart_key = f"cart:{session_id}"

    # Verificar si el usuario está logueado
    user_id = redis_client.hget(f"session:{session_id}", "user_id")
    if not user_id:
        return jsonify({"error": "Debes iniciar sesión antes de confirmar un pedido"}), 401

    cart_items = redis_client.hgetall(cart_key)
    if not cart_items:
        return jsonify({"error": "El carrito está vacío"}), 400

    # Convertir items del carrito en lista de objetos
    items_pedido = []
    total = 0

    productos_coll = db["productos"]
    for product_id_bytes, qty_bytes in cart_items.items():
        product_id_str = product_id_bytes.decode("utf-8")
        qty = int(qty_bytes.decode("utf-8"))

        # Obtener datos del producto desde MongoDB
        producto = productos_coll.find_one({"_id": ObjectId(product_id_str)})
        if producto:
            subtotal = producto["precio"] * qty
            total += subtotal
            items_pedido.append({
                "product_id": product_id_str,
                "nombre": producto["nombre"],
                "cantidad": qty,
                "precio_unitario": producto["precio"],
                "subtotal": subtotal
            })

    # Guardar pedido en MongoDB
    pedidos_coll = db["pedidos"]
    nuevo_pedido = {
        "usuario_id": ObjectId(user_id.decode("utf-8")),
        "items": items_pedido,
        "total": total,
        "estado": "pendiente"
    }
    pedidos_coll.insert_one(nuevo_pedido)

    # Limpiar el carrito en Redis
    redis_client.delete(cart_key)

    return jsonify({"message": "Pedido confirmado", "total": total})

if __name__ == "__main__":
    # Para escuchar en todas las interfaces del contenedor
    app.run(host="0.0.0.0", port=5000, debug=True)
