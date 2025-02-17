# Guía Detallada de Redis y MongoDB en la Aplicación

Este documento explica **cómo** y **dónde** se utilizan **Redis** y **MongoDB** en el contexto de la aplicación de comercio electrónico que hemos construido con Flask. Se describen:

1. Las **funciones** que cumplen cada tecnología.  
2. La **estructura de datos** que se maneja.  
3. Los **endpoints** que hacen uso de Redis y MongoDB.  

---

## Introducción General

- **MongoDB**: Base de datos NoSQL de tipo documental. Almacena, de manera persistente, la información de nuestros usuarios, productos, pedidos, etc.  
- **Redis**: Base de datos en memoria tipo “clave-valor”. Se utiliza principalmente para manejar **sesiones**, **carritos de compra** y cualquier otro dato que sea temporal o necesite acceso de alta velocidad.

En esta aplicación, la combinación de MongoDB y Redis (persistencia poliglota) permite separar responsabilidades:

- **MongoDB** para **datos persistentes** y complejos (CRUD de entidades).  
- **Redis** para **datos volátiles**, con **acceso rápido**, como carritos de compra en curso o sesión de usuario.

---

# Redis en la Aplicación

### ¿Por qué Redis?

Redis es muy eficiente cuando se trata de:

1. **Sesiones**: Almacenar información temporal de los usuarios que están navegando en la web.  
2. **Carritos de compra**: Donde el usuario aún no confirma su pedido, y se hace fácil agregar, eliminar o actualizar productos de manera rápida.

### Estructura de Datos en Redis

Redis trabaja con **claves** y **valores**. En esta app usamos, por ejemplo:

1. **Hash** para guardar un carrito de compras de un usuario:
   - Clave: `cart:{session_id}`  
   - Valor: un **mapa** donde cada “campo” es un `product_id` y el “valor” es la cantidad.

2. **Hash** para guardar la sesión del usuario:
   - Clave: `session:{session_id}`  
   - Valor: un **mapa** con datos básicos (como `user_id`, `user_email`, etc.).

#### Ejemplo de estructura de “carrito”

```
cart:b531076b-e623-4f24-b8c8-6c82fe60b5d7
  ├─ 63f0a7c18a1e3ae2cc502abc: 2
  └─ 63f0a7c18a1e3ae2cc502abd: 1
```
Donde `63f0a7c18a1e3ae2cc502abc` y `63f0a7c18a1e3ae2cc502abd` son **IDs de productos**. El valor numérico indica la cantidad de cada producto.

---

### Endpoints que usan Redis

1. **Autenticación / Sesión**  
   - Endpoint: `POST /login`  
   - Lógica (simplificada):  
     1. El usuario envía sus credenciales (email, por ejemplo).  
     2. Si es válido, generamos un `session_id` (UUID).  
     3. Guardamos en Redis, con la clave `session:{session_id}`, datos del usuario (`user_id`, `user_email`).  
     4. Devolvemos o establecemos la cookie `session_id` en la respuesta HTTP.

2. **Agregar producto al carrito**  
   - Endpoint: `POST /agregar_carrito`  
   - Función: Añade (o incrementa) un producto en el carrito que está en Redis.  
     ```plaintext
     Redis key: cart:{session_id}
     Hash field: {product_id}
     Hash value: Cantidad (int)
     ```
   - Si el producto ya existe, se suma la nueva cantidad.

3. **Ver carrito**  
   - Endpoint: `GET /ver_carrito`  
   - Función: Recupera los datos en la clave `cart:{session_id}` y envía al usuario un JSON con los productos y sus cantidades.

4. **Confirmar pedido**  
   - Endpoint: `POST /confirmar_pedido`  
   - Flujo general:  
     1. Se recuperan los productos (hash) desde `cart:{session_id}`.  
     2. Se crea un documento **pedido** en MongoDB (ver sección más abajo).  
     3. Se elimina la clave `cart:{session_id}` de Redis (carrito vaciado).

---

# MongoDB en la Aplicación

### ¿Por qué MongoDB?

MongoDB es una base de datos NoSQL de tipo **documental** que resulta flexible para manejar la información estructurada o semiestructurada que se genera en un sistema de e-commerce:

- **Usuarios**: Pueden tener distintos atributos, roles, categorías, etc.  
- **Productos**: Almacenan nombre, descripción, precio, stock, etc.  
- **Pedidos**: Almacenan un array de “items” con datos de producto, cantidad, precios, etc.

### Estructura de Datos en MongoDB

En lugar de tablas, MongoDB maneja **colecciones** y **documentos** en formato BSON (Binary JSON). Cada entidad principal de la app es una colección:

1. **usuarios**  
2. **productos**  
3. **pedidos**  

#### Ejemplo de documento en la colección “productos”:

```json
{
  "_id": ObjectId("63f0a7c18a1e3ae2cc502abc"),
  "nombre": "Laptop Gamer",
  "descripcion": "Laptop muy potente",
  "precio": 1500.99,
  "stock": 10
}
```

#### Ejemplo de documento en la colección “pedidos”:

```json
{
  "_id": ObjectId("63f0ad891a1e3ae2cc503fff"),
  "usuario_id": ObjectId("63f0a7c18a1e3ae2cc502aaa"),
  "items": [
    {
      "product_id": "63f0a7c18a1e3ae2cc502abc",
      "nombre": "Laptop Gamer",
      "cantidad": 2,
      "precio_unitario": 1500.99,
      "subtotal": 3001.98
    }
  ],
  "total": 3001.98,
  "estado": "pendiente"
}
```

El campo `_id` (tipo `ObjectId`) se genera automáticamente en MongoDB y es el **identificador único** de cada documento. 

---

### Endpoints que usan MongoDB

#### CRUD de Productos
- **GET /productos**  
  - Lista todos los productos.  
  - Consulta en la colección `productos`.

- **POST /productos**  
  - Crea un nuevo producto.  
  - Inserta un documento en la colección `productos`.

- **GET /productos/<id>**  
  - Obtiene un producto por su `_id`.  
  - Usa `find_one({"_id": ObjectId(id)})` en la colección.

- **PUT /productos/<id>**  
  - Actualiza campos de un producto.  
  - Usa `update_one({"_id": ObjectId(id)}, {"$set": {...}})`.

- **DELETE /productos/<id>**  
  - Elimina un producto por `_id`.

#### CRUD de Usuarios
- **GET /usuarios**  
  - Lista todos los usuarios (colección `usuarios`).

- **POST /usuarios**  
  - Crea un nuevo usuario.

- **GET /usuarios/<id>**  
  - Consulta un usuario por `_id`.

- **PUT /usuarios/<id>**  
  - Actualiza datos de usuario.

- **DELETE /usuarios/<id>**  
  - Elimina usuario por `_id`.

#### CRUD de Pedidos
- **GET /pedidos**  
  - Lista todos los pedidos (colección `pedidos`).

- **POST /pedidos**  
  - Crea un nuevo pedido.  
  - Generalmente se activa cuando el carrito (almacenado en Redis) se “convierte” a pedido.

- **GET /pedidos/<id>**  
  - Consulta un pedido por `_id`.

- **PUT /pedidos/<id>**  
  - Actualiza campos de un pedido (por ejemplo, cambiar `estado` a “pagado”).

- **DELETE /pedidos/<id>**  
  - Elimina un pedido (poco frecuente en producción, pero útil para pruebas).

#### Confirmar Pedido (Uso combinado)
- **POST /confirmar_pedido**  
  1. **Lee** el carrito en Redis (clave `cart:{session_id}`).  
  2. **Genera** el documento pedido en MongoDB (colección `pedidos`).  
  3. **Elimina** el carrito de Redis.

De esta forma, la **persistencia** a largo plazo (el pedido confirmado) queda en MongoDB, mientras que la información volátil (items del carrito) vivió en Redis hasta confirmar la compra.

---

## Resumen

En esta aplicación:

1. **Redis** se centra en:  
   - **Carritos de compra**: Estructura Hash con ID de producto y cantidades.  
   - **Sesiones**: Estructura Hash con datos básicos del usuario (por ejemplo, su ID y su correo).  
   - **Endpoints clave**:  
     - `POST /login` (sesión)  
     - `POST /agregar_carrito` / `GET /ver_carrito` (carrito)  
     - `POST /confirmar_pedido` (borrado de carrito)

2. **MongoDB** se encarga de:  
   - **Usuarios**: Colección `usuarios`.  
   - **Productos**: Colección `productos`.  
   - **Pedidos**: Colección `pedidos`.  
   - **Endpoints CRUD** para crear, leer, actualizar o eliminar documentos en dichas colecciones.  
   - **Confirmar pedido**: Inserta un documento de pedido en la colección `pedidos` y libera el carrito de Redis.

Esta arquitectura logra un **rendimiento** elevado en las operaciones de usuario/carrito y mantiene la **persistencia duradera** en MongoDB para la información verdaderamente importante (usuarios, pedidos, catálogos de productos, etc.).
