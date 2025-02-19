# models.py
from dataclasses import dataclass, field
from typing import List, Dict
from bson import ObjectId

@dataclass
class Usuario:
    _id: ObjectId = field(default_factory=ObjectId)
    nombre: str = ""
    email: str = ""
    categoria: str = ""  # TOP, MEDIUM, LOW

@dataclass
class Producto:
    _id: ObjectId = field(default_factory=ObjectId)
    nombre: str = ""
    descripcion: str = ""
    precio: float = 0.0
    stock: int = 0

@dataclass
class Pedido:
    _id: ObjectId = field(default_factory=ObjectId)
    usuario_id: ObjectId = None
    items: List[Dict] = field(default_factory=list)  # [{product_id, cantidad, precio_unitario}, ...]
    total: float = 0.0
    estado: str = "pendiente"  # pendiente, pagado, enviado, etc.
