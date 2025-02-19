# crud/crud_productos.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
from db_config import get_mongo_client

productos_bp = Blueprint("productos", __name__)

@productos_bp.route("/", methods=["GET", "POST"])
def productos():
    db = get_mongo_client()
    productos_coll = db["productos"]

    if request.method == "GET":
        # READ - obtener todos los productos
        cursor = productos_coll.find({})
        resultados = []
        for prod in cursor:
            prod["_id"] = str(prod["_id"])
            resultados.append(prod)
        return jsonify(resultados), 200

    elif request.method == "POST":
        # CREATE - crear un nuevo producto
        data = request.json
        nuevo_producto = {
            "nombre": data.get("nombre", ""),
            "descripcion": data.get("descripcion", ""),
            "precio": data.get("precio", 0.0),
            "stock": data.get("stock", 0)
        }
        resultado = productos_coll.insert_one(nuevo_producto)
        return jsonify({"_id": str(resultado.inserted_id)}), 201

@productos_bp.route("/<string:producto_id>", methods=["GET", "PUT", "DELETE"])
def producto_por_id(producto_id):
    db = get_mongo_client()
    productos_coll = db["productos"]

    if request.method == "GET":
        # READ - un producto por ID
        producto = productos_coll.find_one({"_id": ObjectId(producto_id)})
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404
        producto["_id"] = str(producto["_id"])
        return jsonify(producto), 200

    elif request.method == "PUT":
        # UPDATE - actualizar producto
        data = request.json
        update_fields = {}
        for campo in ["nombre", "descripcion", "precio", "stock"]:
            if campo in data:
                update_fields[campo] = data[campo]

        if not update_fields:
            return jsonify({"error": "No hay campos para actualizar"}), 400

        resultado = productos_coll.update_one(
            {"_id": ObjectId(producto_id)},
            {"$set": update_fields}
        )
        if resultado.matched_count == 0:
            return jsonify({"error": "Producto no encontrado"}), 404
        return jsonify({"message": "Producto actualizado"}), 200

    elif request.method == "DELETE":
        # DELETE - eliminar producto
        resultado = productos_coll.delete_one({"_id": ObjectId(producto_id)})
        if resultado.deleted_count == 0:
            return jsonify({"error": "Producto no encontrado"}), 404
        return jsonify({"message": "Producto eliminado"}), 200
