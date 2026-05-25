# ============================================================================
# ARCHIVO: tests/integration/test_nuevas_caracteristicas.py
# PROPÓSITO: Pruebas de integración de las nuevas funcionalidades:
#             - Desactivación de cuentas.
#             - Control de permisos/autoría en eventos.
#             - Panel/Rutas CRUD de administración de usuarios.
#             - Flujo de invitaciones a eventos.
# ============================================================================

import pytest
import json
from datetime import date, timedelta
from models.usuario import Usuario
from models.evento import Evento
from database import Database

@pytest.fixture
def business_users():
    """Crea dos usuarios de negocio para pruebas cruzadas."""
    user_a = Usuario(nombre="Usuario Negocio A", email="negocio.a@agendify.com", password="password123", es_admin=0, activo=1)
    user_a.guardar()
    user_b = Usuario(nombre="Usuario Negocio B", email="negocio.b@agendify.com", password="password123", es_admin=0, activo=1)
    user_b.guardar()
    return user_a, user_b

@pytest.fixture
def admin_user():
    """Crea un usuario administrador para pruebas CRUD."""
    admin = Usuario(nombre="Admin Test", email="admin.test@agendify.com", password="adminPassword", es_admin=1, activo=1)
    admin.guardar()
    return admin

def test_login_cuenta_desactivada(client):
    """Prueba que un usuario con cuenta inactiva no pueda iniciar sesión."""
    # 1. Crear un usuario inactivo
    user_inactivo = Usuario(
        nombre="Usuario Inactivo",
        email="inactivo@agendify.com",
        password="password123",
        es_admin=0,
        activo=0  # Cuenta desactivada
    )
    user_inactivo.guardar()

    # 2. Intentar login
    datos_login = {
        "email": "inactivo@agendify.com",
        "password": "password123"
    }
    response = client.post(
        '/api/auth/login',
        data=json.dumps(datos_login),
        content_type='application/json'
    )
    
    assert response.status_code == 403
    res_data = json.loads(response.data)
    assert res_data['status'] == 'error'
    assert "desactivada" in res_data['message']

def test_permisos_creador_eventos(client, business_users):
    """Prueba que sólo el creador de un evento o el admin puedan modificarlo o eliminarlo."""
    user_a, user_b = business_users

    # 1. Autenticar como Usuario A
    with client.session_transaction() as sess:
        sess['user_id'] = user_a.id
        sess['user_name'] = user_a.nombre
        sess['es_admin'] = False

    # 2. Crear evento para Usuario A
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    datos_evento = {
        "titulo": "Evento de Negocio A",
        "fecha": fecha_futura,
        "hora": "10:00",
        "capacidad": 10,
        "creador_id": user_a.id
    }
    res_crear = client.post(
        '/api/eventos',
        data=json.dumps(datos_evento),
        content_type='application/json'
    )
    assert res_crear.status_code == 201
    evento_id = json.loads(res_crear.data)['data']['id']

    # 3. Autenticar como Usuario B (No propietario ni admin)
    with client.session_transaction() as sess:
        sess['user_id'] = user_b.id
        sess['user_name'] = user_b.nombre
        sess['es_admin'] = False

    # 4. Intentar actualizar el evento de A como Usuario B (debe retornar 403)
    datos_update = {
        "titulo": "Intento de Sabotaje",
        "fecha": fecha_futura,
        "hora": "10:00",
        "capacidad": 10
    }
    res_update = client.put(
        f'/api/eventos/{evento_id}',
        data=json.dumps(datos_update),
        content_type='application/json'
    )
    assert res_update.status_code == 403
    assert "permisos" in json.loads(res_update.data)['message']

    # 5. Intentar eliminar el evento de A como Usuario B (debe retornar 403)
    res_delete = client.delete(f'/api/eventos/{evento_id}')
    assert res_delete.status_code == 403

def test_admin_crud_usuarios(client, admin_user, business_users):
    """Prueba que un administrador pueda listar, crear, actualizar y desactivar usuarios."""
    user_a, user_b = business_users

    # 1. Autenticar como Administrador
    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.id
        sess['user_name'] = admin_user.nombre
        sess['es_admin'] = True

    # 2. Listar usuarios (GET /api/admin/usuarios)
    res_list = client.get('/api/admin/usuarios')
    assert res_list.status_code == 200
    usuarios = json.loads(res_list.data)['data']
    assert len(usuarios) >= 3  # Admin + User A + User B
    
    # 3. Crear usuario (POST /api/admin/usuarios)
    datos_crear = {
        "nombre": "Usuario Creado Por Admin",
        "email": "creado.admin@agendify.com",
        "password": "securePassAdmin123",
        "es_admin": 0,
        "activo": 1
    }
    res_crear = client.post(
        '/api/admin/usuarios',
        data=json.dumps(datos_crear),
        content_type='application/json'
    )
    assert res_crear.status_code == 201
    nuevo_id = json.loads(res_crear.data)['data']['id']

    # 4. Actualizar usuario / Desactivarlo (PUT /api/admin/usuarios/<id>)
    datos_update = {
        "nombre": "Usuario Editado Por Admin",
        "email": "creado.admin@agendify.com",
        "es_admin": 0,
        "activo": 0  # Desactivado
    }
    res_update = client.put(
        f'/api/admin/usuarios/{nuevo_id}',
        data=json.dumps(datos_update),
        content_type='application/json'
    )
    assert res_update.status_code == 200
    assert json.loads(res_update.data)['data']['activo'] == 0

    # 5. Eliminar usuario (DELETE /api/admin/usuarios/<id>)
    res_delete = client.delete(f'/api/admin/usuarios/{nuevo_id}')
    assert res_delete.status_code == 200

def test_sistema_invitaciones(client, business_users):
    """Prueba el flujo de invitaciones a un evento y su visibilidad en el dashboard."""
    user_a, user_b = business_users

    # 1. Autenticar como Usuario A (creador)
    with client.session_transaction() as sess:
        sess['user_id'] = user_a.id
        sess['user_name'] = user_a.nombre
        sess['es_admin'] = False

    # 2. Crear evento para Usuario A
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    datos_evento = {
        "titulo": "Evento Compartido A",
        "fecha": fecha_futura,
        "hora": "10:00",
        "capacidad": 10,
        "creador_id": user_a.id
    }
    res_crear = client.post(
        '/api/eventos',
        data=json.dumps(datos_evento),
        content_type='application/json'
    )
    assert res_crear.status_code == 201
    evento_id = json.loads(res_crear.data)['data']['id']

    # 3. Invitar a Usuario B al evento
    datos_invitar = {
        "email": user_b.email
    }
    res_invitar = client.post(
        f'/api/eventos/{evento_id}/invitados',
        data=json.dumps(datos_invitar),
        content_type='application/json'
    )
    assert res_invitar.status_code == 200

    # 4. Obtener invitados del evento y verificar que Usuario B esté incluido
    res_invitados = client.get(f'/api/eventos/{evento_id}/invitados')
    assert res_invitados.status_code == 200
    invitados = json.loads(res_invitados.data)['data']
    assert len(invitados) == 1
    assert invitados[0]['id'] == user_b.id

    # 5. Autenticar como Usuario B (invitado)
    with client.session_transaction() as sess:
        sess['user_id'] = user_b.id
        sess['user_name'] = user_b.nombre
        sess['es_admin'] = False

    # 6. Consultar eventos de B y comprobar que el evento compartido de A le aparece
    res_eventos_b = client.get('/api/eventos')
    assert res_eventos_b.status_code == 200
    eventos_b = json.loads(res_eventos_b.data)['data']['eventos']
    assert len(eventos_b) == 1
    assert eventos_b[0]['id'] == evento_id
    assert eventos_b[0]['titulo'] == "Evento Compartido A"

    # 7. Autenticar nuevamente como Usuario A (creador) para remover la invitación
    with client.session_transaction() as sess:
        sess['user_id'] = user_a.id
        sess['user_name'] = user_a.nombre
        sess['es_admin'] = False

    res_remover = client.delete(f'/api/eventos/{evento_id}/invitados/{user_b.id}')
    assert res_remover.status_code == 200

    # 8. Autenticar como Usuario B y comprobar que ya no ve el evento
    with client.session_transaction() as sess:
        sess['user_id'] = user_b.id
        sess['user_name'] = user_b.nombre
        sess['es_admin'] = False

    res_eventos_b_final = client.get('/api/eventos')
    eventos_b_final = json.loads(res_eventos_b_final.data)['data']['eventos']
    assert len(eventos_b_final) == 0
