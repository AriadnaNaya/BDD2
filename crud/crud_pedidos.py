# crud/crud_pedidos.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
from db_config import get_mongo_client

pedidos_bp = Blueprint("pedidos", __name__)

@pedidos_bp.route("/", methods=["GET", "POST"])
def pedidos():
    db = get_mongo_client()
    pedidos_coll = db["pedidos"]

    if request.method == "GET":
        # READ - obtener todos los pedidos
        cursor = pedidos_coll.find({})
        resultados = []
        for p in cursor:
            p["_id"] = str(p["_id"])
            p["usuario_id"] = str(p["usuario_id"])
            resultados.append(p)
        return jsonify(resultados), 200

    elif request.method == "POST":
        # CREATE - crear un pedido
        data = request.json
        # data es algo como:
        # {
        #   "usuario_id": "63ff...",
        #   "items": [
        #     {"product_id": "...", "cantidad": 2, "precio_unitario": 10, "subtotal": 20},
        #   ],
        #   "total": 20,
        #   "estado": "pendiente"
        # }
        nuevo_pedido = {
            "usuario_id": ObjectId(data["usuario_id"]),
            "items": data.get("items", []),
            "total": data.get("total", 0.0),
            "estado": data.get("estado", "pendiente")
        }
        resultado = pedidos_coll.insert_one(nuevo_pedido)
        return jsonify({"_id": str(resultado.inserted_id)}), 201

@pedidos_bp.route("/<string:pedido_id>", methods=["GET", "PUT", "DELETE"])
def pedido_por_id(pedido_id):
    db = get_mongo_client()
    pedidos_coll = db["pedidos"]

    if request.method == "GET":
        # READ - un pedido por ID
        pedido = pedidos_coll.find_one({"_id": ObjectId(pedido_id)})
        if not pedido:
            return jsonify({"error": "Pedido no encontrado"}), 404
        pedido["_id"] = str(pedido["_id"])
        pedido["usuario_id"] = str(pedido["usuario_id"])
        return jsonify(pedido), 200

    elif request.method == "PUT":
        # UPDATE - actualizar pedido
        data = request.json
        update_fields = {}
        for campo in ["items", "total", "estado"]:
            if campo in data:
                update_fields[campo] = data[campo]

        if not update_fields:
            return jsonify({"error": "No hay campos para actualizar"}), 400

        resultado = pedidos_coll.update_one(
            {"_id": ObjectId(pedido_id)},
            {"$set": update_fields}
        )
        if resultado.matched_count == 0:
            return jsonify({"error": "Pedido no encontrado"}), 404
        return jsonify({"message": "Pedido actualizado"}), 200

    elif request.method == "DELETE":
        # DELETE - eliminar pedido
        resultado = pedidos_coll.delete_one({"_id": ObjectId(pedido_id)})
        if resultado.deleted_count == 0:
            return jsonify({"error": "Pedido no encontrado"}), 404
        return jsonify({"message": "Pedido eliminado"}), 200
