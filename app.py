# app.py
from flask import Flask, session, request, redirect, url_for, render_template, jsonify
from flask_cors import CORS
from db_config import get_mongo_client
from redis_config import get_redis_client
from bson import ObjectId
import uuid
import json
from crud.crud_usuarios import usuarios_bp
from crud.crud_productos import productos_bp
from crud.crud_pedidos import pedidos_bp
import redis

app = Flask(__name__)
app.secret_key = "SECRET_KEY_DE_EJEMPLO"  # Cambiar por algo seguro en producción


# Registrar cada blueprint, asociándolos a un prefijo de URL
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
app.register_blueprint(productos_bp, url_prefix="/productos")
app.register_blueprint(pedidos_bp, url_prefix="/pedidos")


CORS(app, supports_credentials=True)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

# Conexiones a las BD
db = get_mongo_client()
redis_client = get_redis_client()




@app.before_request
def ensure_session():
    if 'user_session_id' not in session:
        session['user_session_id'] = str(uuid.uuid4())

@app.route("/")
def index():
    return "Bienvenido a la plataforma de comercio electrónico."



redis_client = redis.Redis(host="redis", port=6379, db=0)  # Ajusta según tu configuración

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    db = get_mongo_client()
    usuarios_coll = db["usuarios"]
    usuario = usuarios_coll.find_one({"email": email})

    if usuario:
        session_id = session.get("user_session_id")
        # Guardar datos de sesión en Redis
        redis_client.hset(f"session:{session_id}", "user_id", str(usuario["_id"]))
        redis_client.hset(f"session:{session_id}", "user_email", usuario["email"])
        return jsonify({"message": "Usuario logueado", "user": usuario["email"]}), 200
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
    session_id = session.get('user_session_id')
    if not session_id:
        return jsonify({"error": "No hay sesión activa"}), 401

    cart_key = f"cart:{session_id}"
    product_id = request.form.get("product_id")
    cantidad = int(request.form.get("cantidad", 1))

    # Validar que el producto exista en MongoDB
    db = get_mongo_client()
    productos_coll = db["productos"]
    producto = productos_coll.find_one({"_id": ObjectId(product_id)})
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    # Agregar o incrementar la cantidad en el carrito en Redis
    redis_client.hincrby(cart_key, product_id, cantidad)
    # Establecer/renovar el TTL para el carrito (ej. 30 minutos)
    redis_client.expire(cart_key, 1800)

    return jsonify({"message": "Producto agregado al carrito"}), 200


@app.route("/ver_carrito", methods=["GET"])
def ver_carrito():
    session_id = session.get('user_session_id')
    if not session_id:
        return jsonify({"error": "No hay sesión activa"}), 401

    cart_key = f"cart:{session_id}"
    cart_data = redis_client.hgetall(cart_key)

    # Convertir las claves y valores de bytes a strings (y números, en el caso de cantidades)
    carrito = { key.decode("utf-8"): int(value.decode("utf-8")) for key, value in cart_data.items() }

    # Renovar el TTL del carrito
    redis_client.expire(cart_key, 1800)

    return jsonify(carrito), 200

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

@app.route("/ver_sesion", methods=["GET"])
def ver_sesion():
    session_id = session.get("user_session_id")
    if not session_id:
        return jsonify({"error": "No hay sesión activa"}), 401

    # Usar el session_id para consultar la sesión en Redis
    session_key = f"session:{session_id}"
    session_data = redis_client.hgetall(session_key)

    # Convertir las claves y valores de bytes a string
    session_dict = {key.decode("utf-8"): value.decode("utf-8") for key, value in session_data.items()}

    return jsonify(session_dict), 200


if __name__ == "__main__":
    # Para escuchar en todas las interfaces del contenedor
    app.run(host="0.0.0.0", port=5000, debug=True)
