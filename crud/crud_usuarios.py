# crud/crud_usuarios.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
from db_config import get_mongo_client

usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route("/", methods=["GET", "POST"])
def usuarios():
    db = get_mongo_client()
    usuarios_coll = db["usuarios"]

    if request.method == "GET":
        # READ - obtener todos los usuarios
        cursor = usuarios_coll.find({})
        resultados = []
        for usr in cursor:
            usr["_id"] = str(usr["_id"])
            resultados.append(usr)
        return jsonify(resultados), 200

    elif request.method == "POST":
        # CREATE - crear un nuevo usuario
        data = request.json
        nuevo_usuario = {
            "nombre": data.get("nombre", ""),
            "email": data.get("email", ""),
            "categoria": data.get("categoria", "LOW")
        }
        resultado = usuarios_coll.insert_one(nuevo_usuario)
        return jsonify({"_id": str(resultado.inserted_id)}), 201

@usuarios_bp.route("/<string:usuario_id>", methods=["GET", "PUT", "DELETE"])
def usuario_por_id(usuario_id):
    db = get_mongo_client()
    usuarios_coll = db["usuarios"]

    if request.method == "GET":
        # READ - obtener un usuario por ID
        usuario = usuarios_coll.find_one({"_id": ObjectId(usuario_id)})
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        usuario["_id"] = str(usuario["_id"])
        return jsonify(usuario), 200

    elif request.method == "PUT":
        # UPDATE - actualizar un usuario
        data = request.json
        update_fields = {}
        for campo in ["nombre", "email", "categoria"]:
            if campo in data:
                update_fields[campo] = data[campo]

        if not update_fields:
            return jsonify({"error": "No hay campos para actualizar"}), 400

        resultado = usuarios_coll.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": update_fields}
        )
        if resultado.matched_count == 0:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify({"message": "Usuario actualizado"}), 200

    elif request.method == "DELETE":
        # DELETE - eliminar usuario
        resultado = usuarios_coll.delete_one({"_id": ObjectId(usuario_id)})
        if resultado.deleted_count == 0:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify({"message": "Usuario eliminado"}), 200
