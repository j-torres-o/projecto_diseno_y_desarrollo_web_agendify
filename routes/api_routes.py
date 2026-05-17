# ============================================================================
# ARCHIVO: routes/api_routes.py
# PROPÓSITO: Rutas de la API RESTful para operaciones CRUD sobre eventos.
#
# REST (Representational State Transfer) es un estilo de arquitectura
# para diseñar APIs web. Sus principios clave son:
#
#   1. Cada recurso tiene una URL única: /api/eventos, /api/eventos/1
#   2. Se usan verbos HTTP para las operaciones:
#      - GET    → Leer (SELECT)
#      - POST   → Crear (INSERT)
#      - PUT    → Actualizar (UPDATE)
#      - DELETE  → Eliminar (DELETE)
#   3. Las respuestas son en formato JSON (JavaScript Object Notation).
#
# FORMATO DE RESPUESTA ESTANDARIZADO:
# Todas las respuestas de esta API siguen el mismo formato:
#   {
#       "status": "success" | "error",
#       "data": { ... } | [ ... ] | null,
#       "message": "Descripción del resultado"
#   }
# Esto facilita al frontend procesar las respuestas de forma consistente.
# ============================================================================

from flask import Blueprint, request, jsonify
from models.evento import Evento
from mysql.connector import Error as MySQLError

# Blueprint para las rutas de la API.
# url_prefix='/api' hace que todas las rutas definidas aquí
# comiencen con /api automáticamente.
api_bp = Blueprint('api', __name__, url_prefix='/api')


# ============================================================================
# OPERACIÓN: READ (Leer todos los eventos)
# VERBO HTTP: GET
# URL: /api/eventos
# ============================================================================
@api_bp.route('/eventos', methods=['GET'])
def obtener_eventos():
    """
    Obtiene la lista completa de eventos desde la base de datos.

    Este endpoint ejecuta un SELECT * sobre la tabla 'eventos' y
    retorna todos los registros como un arreglo JSON.

    Returns:
        Response: JSON con la lista de eventos.
            - 200 OK: Lista obtenida exitosamente.
            - 500 Internal Server Error: Error de base de datos.
    """
    try:
        eventos_db = Evento.obtener_todos()
        # Convertir registros crudos de base de datos a diccionarios serializables de Evento
        eventos = [Evento.desde_dict(e).to_dict() for e in eventos_db]
        return jsonify({
            'status': 'success',
            'data': eventos,
            'message': f'{len(eventos)} evento(s) encontrado(s).'
        }), 200

    except MySQLError as e:
        return jsonify({
            'status': 'error',
            'data': None,
            'message': f'Error al consultar la base de datos: {str(e)}'
        }), 500


# ============================================================================
# OPERACIÓN: READ (Leer un evento específico)
# VERBO HTTP: GET
# URL: /api/eventos/<id>
# ============================================================================
@api_bp.route('/eventos/<int:id>', methods=['GET'])
def obtener_evento(id):
    """
    Obtiene un evento específico por su ID.

    Args:
        id (int): El ID del evento (viene de la URL).

    Returns:
        Response: JSON con los datos del evento.
            - 200 OK: Evento encontrado.
            - 404 Not Found: No existe un evento con ese ID.
            - 500 Internal Server Error: Error de base de datos.
    """
    try:
        evento_db = Evento.obtener_por_id(id)
        if evento_db:
            # Convertir registro crudo a diccionario serializable de Evento
            evento = Evento.desde_dict(evento_db).to_dict()
            return jsonify({
                'status': 'success',
                'data': evento,
                'message': 'Evento encontrado.'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'data': None,
                'message': f'No se encontró un evento con ID {id}.'
            }), 404

    except MySQLError as e:
        return jsonify({
            'status': 'error',
            'data': None,
            'message': f'Error al consultar la base de datos: {str(e)}'
        }), 500


# ============================================================================
# OPERACIÓN: CREATE (Crear un nuevo evento)
# VERBO HTTP: POST
# URL: /api/eventos
#
# El método POST envía los datos en el CUERPO de la solicitud HTTP,
# no en la URL (como lo haría GET). Esto es fundamental para:
#   1. Seguridad: Los datos no quedan visibles en la barra de direcciones.
#   2. Capacidad: POST puede enviar grandes cantidades de datos.
#   3. Semántica: POST indica "crear algo nuevo" en la convención REST.
# ============================================================================
@api_bp.route('/eventos', methods=['POST'])
def crear_evento():
    """
    Crea un nuevo evento a partir de los datos del formulario.

    El frontend envía los datos como JSON en el cuerpo de la solicitud.
    El servidor los valida, sanitiza y almacena en la base de datos.

    Request Body (JSON):
        {
            "titulo": "Nombre del evento",
            "fecha": "2026-06-01",
            "hora": "10:00",
            "ubicacion": "Sala A",
            "descripcion": "Detalles...",
            "capacidad": 15,
            "tipo_evento": "reunion",
            "prioridad": "alta",
            "recordatorio": true
        }

    Returns:
        Response: JSON con el resultado de la operación.
            - 201 Created: Evento creado exitosamente.
            - 400 Bad Request: Datos inválidos o faltantes.
            - 500 Internal Server Error: Error de base de datos.
    """
    try:
        # request.get_json() extrae el JSON del cuerpo de la solicitud.
        datos = request.get_json()

        if not datos:
            return jsonify({
                'status': 'error',
                'data': None,
                'message': 'No se recibieron datos. Envíe un JSON válido.'
            }), 400

        # Usamos el Factory Method para crear el objeto desde el diccionario.
        evento = Evento.desde_dict(datos)

        # Validamos ANTES de intentar guardar.
        errores = evento.validar()
        if errores:
            return jsonify({
                'status': 'error',
                'data': {'errores': errores},
                'message': 'Los datos no pasaron la validación.'
            }), 400

        # Si la validación pasa, guardamos en la base de datos.
        nuevo_id = evento.guardar()

        return jsonify({
            'status': 'success',
            'data': {'id': nuevo_id, **evento.to_dict()},
            'message': 'Evento creado exitosamente.'
        }), 201

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'data': None,
            'message': str(e)
        }), 400

    except MySQLError as e:
        return jsonify({
            'status': 'error',
            'data': None,
            'message': f'Error de base de datos: {str(e)}'
        }), 500


# ============================================================================
# OPERACIÓN: UPDATE (Actualizar un evento existente)
# VERBO HTTP: PUT
# URL: /api/eventos/<id>
# ============================================================================
@api_bp.route('/eventos/<int:id>', methods=['PUT'])
def actualizar_evento(id):
    """
    Actualiza un evento existente con nuevos datos.

    Args:
        id (int): El ID del evento a actualizar (viene de la URL).

    Returns:
        Response: JSON con el resultado de la actualización.
            - 200 OK: Evento actualizado exitosamente.
            - 400 Bad Request: Datos inválidos.
            - 404 Not Found: Evento no encontrado.
            - 500 Internal Server Error: Error de base de datos.
    """
    try:
        # Verificamos que el evento existe antes de intentar actualizarlo.
        evento_existente = Evento.obtener_por_id(id)
        if not evento_existente:
            return jsonify({
                'status': 'error',
                'data': None,
                'message': f'No se encontró un evento con ID {id}.'
            }), 404

        datos = request.get_json()
        if not datos:
            return jsonify({
                'status': 'error',
                'data': None,
                'message': 'No se recibieron datos para actualizar.'
            }), 400

        # Creamos un objeto Evento con los nuevos datos Y el ID existente.
        evento = Evento.desde_dict(datos)
        evento.id = id

        errores = evento.validar()
        if errores:
            return jsonify({
                'status': 'error',
                'data': {'errores': errores},
                'message': 'Los datos no pasaron la validación.'
            }), 400

        evento.actualizar()

        return jsonify({
            'status': 'success',
            'data': evento.to_dict(),
            'message': 'Evento actualizado exitosamente.'
        }), 200

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'data': None,
            'message': str(e)
        }), 400

    except MySQLError as e:
        return jsonify({
            'status': 'error',
            'data': None,
            'message': f'Error de base de datos: {str(e)}'
        }), 500


# ============================================================================
# OPERACIÓN: DELETE (Eliminar un evento)
# VERBO HTTP: DELETE
# URL: /api/eventos/<id>
# ============================================================================
@api_bp.route('/eventos/<int:id>', methods=['DELETE'])
def eliminar_evento(id):
    """
    Elimina un evento de la base de datos por su ID.

    Args:
        id (int): El ID del evento a eliminar (viene de la URL).

    Returns:
        Response: JSON con el resultado de la eliminación.
            - 200 OK: Evento eliminado exitosamente.
            - 404 Not Found: Evento no encontrado.
            - 500 Internal Server Error: Error de base de datos.
    """
    try:
        # Verificamos que el evento existe antes de eliminarlo.
        evento_existente = Evento.obtener_por_id(id)
        if not evento_existente:
            return jsonify({
                'status': 'error',
                'data': None,
                'message': f'No se encontró un evento con ID {id}.'
            }), 404

        Evento.eliminar(id)

        return jsonify({
            'status': 'success',
            'data': None,
            'message': f'Evento con ID {id} eliminado exitosamente.'
        }), 200

    except MySQLError as e:
        return jsonify({
            'status': 'error',
            'data': None,
            'message': f'Error de base de datos: {str(e)}'
        }), 500
