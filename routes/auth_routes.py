# ============================================================================
# ARCHIVO: routes/auth_routes.py
# PROPÓSITO: Rutas de autenticación y control de accesos de Agendify.
#
# Este controlador (Controller en la arquitectura MVC) expone endpoints RESTful
# para el flujo de autenticación de usuarios. Utiliza `flask.session` para
# gestionar la persistencia del estado (sesiones en el lado del servidor) y
# proteger contra accesos no autorizados.
#
# CARACTERÍSTICAS DE SEGURIDAD IMPLEMENTADAS:
#   1. Decorador `login_required` reutilizable para proteger rutas.
#   2. Criptografía mediante Hashing de contraseñas de un solo sentido.
#   3. Duración de sesión configurable y cookies HTTPOnly (protección XSS).
# ============================================================================

from flask import Blueprint, request, jsonify, session
from functools import wraps
from models.usuario import Usuario

# Blueprint para centralizar las rutas de autenticación.
# El prefijo '/api/auth' agrupa todas estas rutas de forma limpia.
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def login_required(f):
    """
    Decorador personalizado para la protección de accesos.

    Intercepta las peticiones dirigidas a endpoints sensibles. Si el cliente
    no posee una sesión activa o la cuenta ha sido desactivada,
    deniega la acción devolviendo un error HTTP 401 (No Autorizado) en JSON.

    Args:
        f (function): La función del endpoint original a decorar.

    Returns:
        function: Función decorada que evalúa los accesos.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # NOTA DE SEGURIDAD:
        # Se verifica la presencia del ID de usuario en el diccionario de sesiones
        if 'user_id' not in session:
            return jsonify({
                'status': 'error',
                'data': None,
                'message': 'No autorizado. Por favor inicie sesión para continuar.'
            }), 401
        
        # Verificar si la cuenta sigue activa en la base de datos
        usuario_db = Usuario.obtener_por_id(session['user_id'])
        if not usuario_db or not usuario_db.get('activo'):
            session.clear()
            return jsonify({
                'status': 'error',
                'data': None,
                'message': 'Su cuenta está inactiva o no existe. Sesión cerrada.'
            }), 401
            
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint para el autoregistro de nuevos usuarios.

    Recibe los datos en JSON, los valida en backend y almacena al usuario con
    su contraseña encriptada (hashing scrypt irreversible).

    Request Body (JSON):
        {
            "nombre": "Nombre Completo",
            "email": "correo@ejemplo.com",
            "password": "mi_clave_segura"
        }

    Returns:
        Response: JSON con el resultado del registro.
            - 201 Created: Registro exitoso.
            - 400 Bad Request: Errores de validación o datos faltantes.
            - 500 Internal Error: Error inesperado del servidor.
    """
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({
                'status': 'error',
                'data': None,
                'message': 'No se recibieron datos en el cuerpo de la solicitud.'
            }), 400

        # Instanciamos el modelo con los datos del JSON
        usuario = Usuario.desde_dict(datos)
        
        # Validamos integridad y formato en el lado del Servidor
        errores = usuario.validar()
        if errores:
            return jsonify({
                'status': 'error',
                'data': {'errores': errores},
                'message': 'Los datos proporcionados no pasaron las validaciones de seguridad.'
            }), 400

        # Verificamos si ya existe el correo (evitamos duplicados)
        if Usuario.obtener_por_email(usuario.email):
            return jsonify({
                'status': 'error',
                'data': None,
                'message': 'El correo electrónico ingresado ya se encuentra registrado.'
            }), 400

        # Guardamos en BD y recuperamos el ID generado
        nuevo_id = usuario.guardar()
        
        return jsonify({
            'status': 'success',
            'data': {
                'id': nuevo_id,
                'nombre': usuario.nombre,
                'email': usuario.email
            },
            'message': 'Registro de usuario exitoso.'
        }), 201

    except Exception as e:
        return jsonify({
            'status': 'error',
            'data': None,
            'message': f'Error interno durante el registro: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint para el inicio de sesión y autenticación de usuarios.

    Valida las credenciales ingresadas comparándolas de forma segura con
    la base de datos. Si son válidas, establece los datos de sesión correspondientes.

    Request Body (JSON):
        {
            "email": "correo@ejemplo.com",
            "password": "mi_clave_segura"
        }

    Returns:
        Response: JSON confirmando el acceso.
            - 200 OK: Autenticación aprobada y sesión iniciada.
            - 400 Bad Request: Campos incompletos.
            - 401 Unauthorized: Correo no existe o contraseña incorrecta.
            - 500 Internal Error: Excepción del servidor.
    """
    try:
        datos = request.get_json()
        if not datos or not datos.get('email') or not datos.get('password'):
            return jsonify({
                'status': 'error',
                'data': None,
                'message': 'Las credenciales de acceso están incompletas.'
            }), 400

        # Buscamos al usuario por correo
        usuario = Usuario.obtener_por_email(datos['email'])
        
        # Validamos existencia y contraseña de forma criptográfica
        if usuario and usuario.verificar_password(datos['password']):
            if not usuario.activo:
                return jsonify({
                    'status': 'error',
                    'data': None,
                    'message': 'Su cuenta ha sido desactivada. Por favor contacte al administrador.'
                }), 403
                
            # ESTABLECIMIENTO DE SESIÓN:
            # Flask cifra esta información en una cookie del cliente firmada
            # mediante la SECRET_KEY del servidor.
            session['user_id'] = usuario.id
            session['user_name'] = usuario.nombre
            session['es_admin'] = bool(usuario.es_admin)
            
            # session.permanent activa el tiempo de expiración definido en config.py
            session.permanent = True
            
            return jsonify({
                'status': 'success',
                'data': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'es_admin': bool(usuario.es_admin)
                },
                'message': 'Inicio de sesión exitoso. Bienvenido a Agendify.'
            }), 200
        else:
            # Por seguridad, el mensaje de error es genérico ("Credenciales inválidas")
            # para no darle pistas a atacantes sobre qué campo falló exactamente.
            return jsonify({
                'status': 'error',
                'data': None,
                'message': 'El correo electrónico o la contraseña son incorrectos.'
            }), 401

    except Exception as e:
        return jsonify({
            'status': 'error',
            'data': None,
            'message': f'Error interno del servidor en inicio de sesión: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Endpoint para el cierre de sesión seguro.

    Limpia por completo las variables del diccionario de sesión del servidor
    y descarta la cookie firmada del cliente.

    Returns:
        Response: JSON confirmando la salida.
            - 200 OK: Sesión destruida exitosamente.
    """
    # session.clear() elimina toda la data asociada (user_id, user_name) de esta sesión
    session.clear()
    return jsonify({
        'status': 'success',
        'data': None,
        'message': 'Sesión cerrada correctamente. Gracias por usar Agendify.'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    """
    Endpoint para obtener la información del usuario autenticado en la sesión actual.

    Sirve para sincronizar el estado global del frontend al recargar la página.

    Returns:
        Response: JSON con los datos no sensibles del usuario.
            - 200 OK: Sesión válida.
            - 404 Not Found: El usuario guardado en sesión ya no existe en base de datos.
    """
    usuario = Usuario.obtener_por_id(session['user_id'])
    if usuario:
        # Convertimos los datos a una estructura de diccionario segura
        usuario_dict = Usuario.desde_dict(usuario).to_dict()
        return jsonify({
            'status': 'success',
            'data': usuario_dict,
            'message': 'Datos del usuario de la sesión actual obtenidos.'
        }), 200
    
    return jsonify({
        'status': 'error',
        'data': None,
        'message': 'El usuario actual no existe en el sistema.'
    }), 404
