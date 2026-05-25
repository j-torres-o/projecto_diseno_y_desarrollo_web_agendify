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
from routes.auth_routes import login_required
from models.evento import Evento
from database import Database
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
@login_required
def obtener_eventos():
    """
    Obtiene la lista de eventos de forma paginada y segura.

    Este endpoint requiere que el usuario haya iniciado sesión (verificado por
    @login_required). Lee los parámetros 'page' y 'limit' desde los argumentos de la
    URL (?page=1&limit=5), realiza validaciones preventivas en el lado del servidor 
    para mitigar valores maliciosos (límites extremos) y realiza la consulta optimizada.

    Query Parameters:
        page (int, opcional): Página actual a cargar. Por defecto es 1.
        limit (int, opcional): Cantidad de eventos por página. Por defecto es 10. Máximo es 50.

    Returns:
        Response: Objeto JSON con el listado de eventos de la página y metadatos del estado
            de la paginación (total, total_pages, página actual, etc.).
            - 200 OK: Operación exitosa. Retorna data estructurada.
            - 401 Unauthorized: El cliente no posee una sesión iniciada.
            - 500 Internal Error: Excepción en conexión o base de datos.
    """
    try:
        # Extraemos los parámetros de paginación del request GET.
        # type=int intenta forzar el casteo; si no es entero, retorna None o el valor por defecto.
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # --- CONTROL DE INYECCIÓN Y EXCESO DE MEMORIA ---
        # 1. Aseguramos que la página nunca sea menor a 1.
        if page < 1: 
            page = 1
        # 2. Aseguramos que el límite no sea negativo.
        if limit < 1: 
            limit = 10
        # 3. Establecemos un TOPE máximo (50) para prevenir ataques DDoS de consumo de memoria
        # si un cliente solicita millones de registros de un solo golpe.
        if limit > 50: 
            limit = 50
        
        # Capturamos filtros opcionales de búsqueda
        fecha = request.args.get('fecha', '').strip() or None
        tipo_evento = request.args.get('tipo_evento', '').strip() or None
        prioridad = request.args.get('prioridad', '').strip() or None
        creador_id = request.args.get('creador_id', type=int)
        
        # Si es administrador, tiene acceso a todos los eventos de todos los usuarios
        if session.get('es_admin'):
            eventos_db, total = Evento.obtener_paginados(page, limit, fecha, tipo_evento, prioridad, creador_id)
        else:
            eventos_db, total = Evento.obtener_paginados_por_usuario(session['user_id'], page, limit, fecha, tipo_evento, prioridad, creador_id)
        
        # Transformamos la lista cruda de registros BD a modelos y luego a diccionarios JSON-serializables
        eventos = [Evento.desde_dict(e).to_dict() for e in eventos_db]
        
        # Fórmula matemática para determinar la cantidad de páginas totales: división con redondeo hacia arriba
        total_pages = (total + limit - 1) // limit

        # Retornamos estructura estandarizada de API de Agendify
        return jsonify({
            'status': 'success',
            'data': {
                'eventos': eventos,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': total_pages
                }
            },
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
@login_required
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
            # SEGURIDAD: Si no es admin, debe ser el creador o un invitado
            if not session.get('es_admin') and evento_db['creador_id'] != session['user_id']:
                evento_obj = Evento.desde_dict(evento_db)
                invitados = [inv['id'] for inv in evento_obj.obtener_invitados()]
                if session['user_id'] not in invitados:
                    return jsonify({
                        'status': 'error',
                        'data': None,
                        'message': 'No tiene autorización para visualizar este evento.'
                    }), 403
            
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
@login_required
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

        # Inyectamos el ID del usuario creador desde la sesión activa
        datos['creador_id'] = session['user_id']

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
@login_required
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

        # SEGURIDAD: Solo el creador del evento (o un administrador) puede modificarlo
        if evento_existente['creador_id'] != session['user_id'] and not session.get('es_admin'):
            return jsonify({
                'status': 'error',
                'data': None,
                'message': 'No tiene permisos para modificar este evento.'
            }), 403

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
        evento.creador_id = evento_existente['creador_id']  # Preservar creador original

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
@login_required
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

        # SEGURIDAD: Solo el creador del evento (o un administrador) puede eliminarlo
        if evento_existente['creador_id'] != session['user_id'] and not session.get('es_admin'):
            return jsonify({
                'status': 'error',
                'data': None,
                'message': 'No tiene permisos para eliminar este evento.'
            }), 403

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


# ============================================================================
# ENDPOINTS DE ADMINISTRACIÓN DE USUARIOS (CRUD para administradores)
# ============================================================================

from models.usuario import Usuario

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'message': 'No autorizado.'
            }), 401
        usuario = Usuario.obtener_por_id(session['user_id'])
        if not usuario or not usuario.get('es_admin') or not usuario.get('activo'):
            return jsonify({
                'status': 'error',
                'message': 'Requiere permisos de administrador.'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

from flask import session

@api_bp.route('/admin/usuarios', methods=['GET'])
@admin_required
def admin_listar_usuarios():
    try:
        # Recuperamos la lista de todos los usuarios
        usuarios_db = Usuario.obtener_todos()
        usuarios = [Usuario.desde_dict(u).to_dict() for u in usuarios_db]
        return jsonify({
            'status': 'success',
            'data': usuarios,
            'message': f'{len(usuarios)} usuario(s) encontrado(s).'
        }), 200
    except MySQLError as e:
        return jsonify({
            'status': 'error',
            'message': f'Error de base de datos: {str(e)}'
        }), 500

@api_bp.route('/admin/usuarios', methods=['POST'])
@admin_required
def admin_crear_usuario():
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({'status': 'error', 'message': 'JSON vacío.'}), 400
        
        usuario = Usuario.desde_dict(datos)
        errores = usuario.validar()
        if errores:
            return jsonify({'status': 'error', 'data': {'errores': errores}, 'message': 'Validación fallida.'}), 400
            
        if Usuario.obtener_por_email(usuario.email):
            return jsonify({'status': 'error', 'message': 'El correo ya está registrado.'}), 400
            
        nuevo_id = usuario.guardar()
        return jsonify({
            'status': 'success',
            'data': {'id': nuevo_id, **usuario.to_dict()},
            'message': 'Usuario creado exitosamente.'
        }), 201
    except MySQLError as e:
        return jsonify({'status': 'error', 'message': f'Error de base de datos: {str(e)}'}), 500

@api_bp.route('/admin/usuarios/<int:id>', methods=['PUT'])
@admin_required
def admin_actualizar_usuario(id):
    try:
        usuario_db = Usuario.obtener_por_id(id)
        if not usuario_db:
            return jsonify({'status': 'error', 'message': 'Usuario no encontrado.'}), 404
            
        datos = request.get_json()
        if not datos:
            return jsonify({'status': 'error', 'message': 'JSON vacío.'}), 400
            
        password_a_usar = datos.get('password')
        hash_a_usar = usuario_db['password_hash']
        
        usuario = Usuario(
            nombre=datos.get('nombre', usuario_db['nombre']),
            email=datos.get('email', usuario_db['email']),
            password=password_a_usar if password_a_usar else None,
            password_hash=hash_a_usar if not password_a_usar else None,
            es_admin=datos.get('es_admin', usuario_db['es_admin']),
            activo=datos.get('activo', usuario_db['activo']),
            id=id
        )
        
        errores = []
        if not usuario.nombre or len(usuario.nombre) < 3:
            errores.append("El nombre debe tener al menos 3 caracteres.")
        if not usuario.email or "@" not in usuario.email:
            errores.append("Formato de correo electrónico inválido.")
        if password_a_usar and len(password_a_usar) < 6:
            errores.append("La contraseña debe tener al menos 6 caracteres.")
            
        if errores:
            return jsonify({'status': 'error', 'data': {'errores': errores}, 'message': 'Validación fallida.'}), 400
            
        if usuario.email != usuario_db['email']:
            if Usuario.obtener_por_email(usuario.email):
                return jsonify({'status': 'error', 'message': 'El correo ya está registrado.'}), 400
                
        usuario.actualizar()
        return jsonify({
            'status': 'success',
            'data': usuario.to_dict(),
            'message': 'Usuario actualizado exitosamente.'
        }), 200
    except MySQLError as e:
        return jsonify({'status': 'error', 'message': f'Error de base de datos: {str(e)}'}), 500

@api_bp.route('/admin/usuarios/<int:id>', methods=['DELETE'])
@admin_required
def admin_eliminar_usuario(id):
    try:
        usuario_db = Usuario.obtener_por_id(id)
        if not usuario_db:
            return jsonify({'status': 'error', 'message': 'Usuario no encontrado.'}), 404
            
        if id == session['user_id']:
            return jsonify({'status': 'error', 'message': 'No puede eliminarse a sí mismo.'}), 400
            
        Usuario.eliminar(id)
        return jsonify({
            'status': 'success',
            'message': 'Usuario eliminado exitosamente.'
        }), 200
    except MySQLError as e:
        return jsonify({'status': 'error', 'message': f'Error de base de datos: {str(e)}'}), 500


# ============================================================================
# ENDPOINTS DE INVITACIONES A EVENTOS
# ============================================================================

@api_bp.route('/eventos/<int:id>/invitados', methods=['GET'])
@login_required
def obtener_invitados(id):
    try:
        evento_db = Evento.obtener_por_id(id)
        if not evento_db:
            return jsonify({'status': 'error', 'message': 'Evento no encontrado.'}), 404
            
        evento = Evento.desde_dict(evento_db)
        invitados = evento.obtener_invitados()
        return jsonify({
            'status': 'success',
            'data': invitados,
            'message': f'{len(invitados)} invitado(s) encontrado(s).'
        }), 200
    except MySQLError as e:
        return jsonify({'status': 'error', 'message': f'Error de base de datos: {str(e)}'}), 500

@api_bp.route('/eventos/<int:id>/invitados', methods=['POST'])
@login_required
def invitar_usuario(id):
    try:
        evento_db = Evento.obtener_por_id(id)
        if not evento_db:
            return jsonify({'status': 'error', 'message': 'Evento no encontrado.'}), 404
        if evento_db['creador_id'] != session['user_id'] and not session.get('es_admin'):
            return jsonify({'status': 'error', 'message': 'Solo el creador puede invitar usuarios.'}), 403
            
        datos = request.get_json()
        email = datos.get('email')
        if not email:
            return jsonify({'status': 'error', 'message': 'El correo electrónico es obligatorio.'}), 400
            
        invitado = Usuario.obtener_por_email(email)
        if not invitado:
            return jsonify({'status': 'error', 'message': 'No existe ningún usuario registrado con ese correo.'}), 404
            
        if invitado.id == evento_db['creador_id']:
            return jsonify({'status': 'error', 'message': 'El creador ya forma parte del evento.'}), 400
            
        evento = Evento.desde_dict(evento_db)
        evento.agregar_invitado(invitado.id)
        return jsonify({
            'status': 'success',
            'message': f'Usuario {invitado.nombre} invitado correctamente.'
        }), 200
    except MySQLError as e:
        return jsonify({'status': 'error', 'message': f'Error de base de datos: {str(e)}'}), 500

@api_bp.route('/eventos/<int:id>/invitados/<int:usuario_id>', methods=['DELETE'])
@login_required
def eliminar_invitado(id, usuario_id):
    try:
        evento_db = Evento.obtener_por_id(id)
        if not evento_db:
            return jsonify({'status': 'error', 'message': 'Evento no encontrado.'}), 404
        if evento_db['creador_id'] != session['user_id'] and not session.get('es_admin'):
            return jsonify({'status': 'error', 'message': 'Solo el creador puede remover invitados.'}), 403
            
        evento = Evento.desde_dict(evento_db)
        evento.eliminar_invitado(usuario_id)
        return jsonify({
            'status': 'success',
            'message': 'Invitación removida exitosamente.'
        }), 200
    except MySQLError as e:
        return jsonify({'status': 'error', 'message': f'Error de base de datos: {str(e)}'}), 500


# ============================================================================
# ENDPOINT: BÚSQUEDA RÁPIDA DE USUARIOS PARA FILTROS (AUTOCOMPLETE)
# ============================================================================
@api_bp.route('/usuarios/buscar', methods=['GET'])
@login_required
def buscar_usuarios():
    """
    Endpoint para buscar usuarios de manera interactiva mediante LIKE en MySQL
    sobre su nombre o correo electrónico. Utilizado por el frontend para poblar
    el listado de sugerencias de organizadores al vuelo.
    """
    try:
        q = request.args.get('q', '').strip()
        if not q or len(q) < 2:
            return jsonify({
                'status': 'success',
                'data': [],
                'message': 'Ingrese al menos 2 caracteres para realizar la búsqueda.'
            }), 200
        
        # Filtramos usuarios que estén activos
        query = """
            SELECT id, nombre, email 
            FROM usuarios 
            WHERE (nombre LIKE %s OR email LIKE %s) AND activo = 1 
            LIMIT 8
        """
        like_param = f"%{q}%"
        usuarios = Database.execute_query(query, (like_param, like_param), fetch_all=True)
        return jsonify({
            'status': 'success',
            'data': usuarios if usuarios else [],
            'message': f'{len(usuarios) if usuarios else 0} usuario(s) encontrado(s).'
        }), 200
    except MySQLError as e:
        return jsonify({
            'status': 'error',
            'data': None,
            'message': f'Error al buscar usuarios en la base de datos: {str(e)}'
        }), 500

