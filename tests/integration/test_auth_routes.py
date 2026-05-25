# ============================================================================
# ARCHIVO: tests/integration/test_auth_routes.py
# PROPÓSITO: Pruebas de integración de endpoints de autenticación y sesión.
# ============================================================================

import pytest
import json
from models.usuario import Usuario

def test_api_registro_exitoso(client):
    """Prueba el registro exitoso de un nuevo usuario a través de la API POST."""
    datos_registro = {
        "nombre": "Nuevo Usuario",
        "email": "nuevo.usuario@agendify.com",
        "password": "mySecurePassword123"
    }
    
    response = client.post(
        '/api/auth/register',
        data=json.dumps(datos_registro),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    res_data = json.loads(response.data)
    assert res_data['status'] == 'success'
    assert "Registro de usuario exitoso." in res_data['message']
    assert 'id' in res_data['data']
    assert res_data['data']['email'] == "nuevo.usuario@agendify.com"


def test_api_registro_email_duplicado(client, setup_user):
    """Prueba que el sistema no permita registrar dos usuarios con el mismo correo."""
    datos_registro = {
        "nombre": "Otro Nombre",
        "email": setup_user.email,  # Mismo email que el de setup_user
        "password": "password123"
    }
    
    response = client.post(
        '/api/auth/register',
        data=json.dumps(datos_registro),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    res_data = json.loads(response.data)
    assert res_data['status'] == 'error'
    assert "ya se encuentra registrado" in res_data['message']


def test_api_registro_datos_invalidos(client):
    """Prueba que el validador detenga registros incompletos o inválidos."""
    datos_registro = {
        "nombre": "Ab",  # Muy corto
        "email": "email-invalido",
        "password": "12"  # Muy corta
    }
    
    response = client.post(
        '/api/auth/register',
        data=json.dumps(datos_registro),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    res_data = json.loads(response.data)
    assert res_data['status'] == 'error'
    assert 'errores' in res_data['data']
    errores = res_data['data']['errores']
    assert any("El nombre debe tener entre 3 y 100 caracteres." in err for err in errores)
    assert any("El formato del correo electrónico es inválido." in err for err in errores)
    assert any("La contraseña debe tener al menos 6 caracteres por seguridad." in err for err in errores)


def test_api_login_exitoso(client, setup_user):
    """Prueba el inicio de sesión exitoso con credenciales correctas."""
    datos_login = {
        "email": setup_user.email,
        "password": "password123"
    }
    
    response = client.post(
        '/api/auth/login',
        data=json.dumps(datos_login),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    res_data = json.loads(response.data)
    assert res_data['status'] == 'success'
    assert "Inicio de sesión exitoso." in res_data['message']
    assert res_data['data']['email'] == setup_user.email
    
    # Verificar que el cliente tenga las variables de sesión establecidas
    with client.session_transaction() as sess:
        assert sess['user_id'] == setup_user.id
        assert sess['user_name'] == setup_user.nombre


def test_api_login_credenciales_incorrectas(client, setup_user):
    """Prueba que el login falle con contraseña errónea o correo no registrado."""
    # 1. Contraseña incorrecta
    datos_login = {
        "email": setup_user.email,
        "password": "wrong_password"
    }
    response = client.post('/api/auth/login', data=json.dumps(datos_login), content_type='application/json')
    assert response.status_code == 401
    assert "incorrectos" in json.loads(response.data)['message']

    # 2. Correo inexistente
    datos_login2 = {
        "email": "noexist@agendify.com",
        "password": "password123"
    }
    response2 = client.post('/api/auth/login', data=json.dumps(datos_login2), content_type='application/json')
    assert response2.status_code == 401
    assert "incorrectos" in json.loads(response2.data)['message']


def test_api_session_me(client, setup_user):
    """Prueba el endpoint /me para obtener datos del usuario logueado o responder 401."""
    # 1. Sin sesión activa
    response_anonimo = client.get('/api/auth/me')
    assert response_anonimo.status_code == 401
    assert "No autorizado" in json.loads(response_anonimo.data)['message']

    # 2. Con sesión activa (Simulada por session_transaction)
    with client.session_transaction() as sess:
        sess['user_id'] = setup_user.id
        sess['user_name'] = setup_user.nombre

    response_logueado = client.get('/api/auth/me')
    assert response_logueado.status_code == 200
    res_data = json.loads(response_logueado.data)
    assert res_data['status'] == 'success'
    assert res_data['data']['email'] == setup_user.email


def test_api_logout(client, setup_user):
    """Prueba que el cierre de sesión limpie las cookies y variables en el servidor."""
    # 1. Iniciar sesión simulada
    with client.session_transaction() as sess:
        sess['user_id'] = setup_user.id
        sess['user_name'] = setup_user.nombre

    # 2. Ejecutar logout
    response = client.post('/api/auth/logout')
    assert response.status_code == 200
    assert "Sesión cerrada correctamente" in json.loads(response.data)['message']

    # 3. Comprobar que ya no hay sesión en la transacción
    with client.session_transaction() as sess:
        assert 'user_id' not in sess
        assert 'user_name' not in sess
