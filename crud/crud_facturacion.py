from flask import Blueprint, request, jsonify
from bson import ObjectId
from db_config import get_mongo_client

facturas_bp = Blueprint("facturas", __name__)

db = get_mongo_client()
facturas_coll = db["facturas"]
pagos_coll = db["pagos"]

@facturas_bp.route("/", methods=["GET", "POST"])
def facturas():
    # Lista todas las facturas almacenadas
    if request.method == "GET":
        cursor = facturas_coll.find({})
        resultados = []
        for factura in cursor:
            factura["_id"] = str(factura["_id"])
            factura["usuario_id"] = str(factura["usuario_id"])
            resultados.append(factura)
        return jsonify(resultados), 200

    # Crea una nueva factura con estado inicial pendiente
    elif request.method == "POST":
        data = request.json
        nueva_factura = {
            "usuario_id": ObjectId(data["usuario_id"]),
            "monto": data.get("monto", 0.0),
            "estado": data.get("estado", "pendiente"),
            "fecha": data.get("fecha", "")
        }
        resultado = facturas_coll.insert_one(nueva_factura)
        return jsonify({"_id": str(resultado.inserted_id)}), 201

@facturas_bp.route("/<string:factura_id>", methods=["GET", "PUT", "DELETE"])
def factura_por_id(factura_id):
    # Obtiene una factura por ID
    if request.method == "GET":
        factura = facturas_coll.find_one({"_id": ObjectId(factura_id)})
        if not factura:
            return jsonify({"error": "Factura no encontrada"}), 404
        factura["_id"] = str(factura["_id"])
        factura["usuario_id"] = str(factura["usuario_id"])
        return jsonify(factura), 200

    # Actualizar campos de una factura por ID
    elif request.method == "PUT":
        data = request.json
        update_fields = {}
        for campo in ["monto", "estado", "fecha"]:
            if campo in data:
                update_fields[campo] = data[campo]

        if not update_fields:
            return jsonify({"error": "No hay campos para actualizar"}), 400

        resultado = facturas_coll.update_one(
            {"_id": ObjectId(factura_id)},
            {"$set": update_fields}
        )
        if resultado.matched_count == 0:
            return jsonify({"error": "Factura no encontrada"}), 404
        return jsonify({"message": "Factura actualizada"}), 200

    # Eliminar una factura por ID
    elif request.method == "DELETE":
        resultado = facturas_coll.delete_one({"_id": ObjectId(factura_id)})
        if resultado.deleted_count == 0:
            return jsonify({"error": "Factura no encontrada"}), 404
        return jsonify({"message": "Factura eliminada"}), 200

# Registra pago asociado a factura y actualiza estado a pagado
@facturas_bp.route("/<string:factura_id>/pago", methods=["POST"])
def registrar_pago(factura_id):
    data = request.json
    pago = {
        "factura_id": ObjectId(factura_id),
        "monto": data.get("monto", 0.0),
        "fecha": data.get("fecha", "")
    }
    resultado = pagos_coll.insert_one(pago)
    facturas_coll.update_one(
        {"_id": ObjectId(factura_id)},
        {"$set": {"estado": "pagado"}}
    )
    return jsonify({"_id": str(resultado.inserted_id), "message": "Pago registrado"}), 201

# Lista pagos asociados a una factura
@facturas_bp.route("/<string:factura_id>/pagos", methods=["GET"])
def listar_pagos(factura_id):
    cursor = pagos_coll.find({"factura_id": ObjectId(factura_id)})
    pagos = []
    for pago in cursor:
        pago["_id"] = str(pago["_id"])
        pago["factura_id"] = str(pago["factura_id"])
        pagos.append(pago)
    return jsonify(pagos), 200
