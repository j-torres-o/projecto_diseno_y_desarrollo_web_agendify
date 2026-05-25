# ============================================================================
# ARCHIVO: tests/integration/test_api_routes.py
# PROPÓSITO: Pruebas de integración de la API REST de Agendify.
# ============================================================================

import pytest
import json
from datetime import date, timedelta

def test_api_rutas_protegidas(client):
    """Prueba que el acceso sin sesión activa devuelva 401 No Autorizado."""
    response = client.get('/api/eventos')
    assert response.status_code == 401
    
    response_post = client.post('/api/eventos', data='{}', content_type='application/json')
    assert response_post.status_code == 401

def test_api_crear_evento_valido(auth_client):
    """Prueba la creación exitosa de un evento a través de la API POST."""
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    datos_evento = {
        "titulo": "Reunión de Integración",
        "fecha": fecha_futura,
        "hora": "10:30",
        "ubicacion": "Sala de Reuniones Virtual",
        "descripcion": "Discusión sobre los resultados de pruebas integradas",
        "capacidad": 20,
        "tipo_evento": "reunion",
        "prioridad": "alta",
        "recordatorio": True
    }
    
    response = auth_client.post(
        '/api/eventos',
        data=json.dumps(datos_evento),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    res_data = json.loads(response.data)
    assert res_data['status'] == 'success'
    assert res_data['message'] == 'Evento creado exitosamente.'
    assert 'id' in res_data['data']
    assert res_data['data']['titulo'] == "Reunión de Integración"
    assert res_data['data']['capacidad'] == 20


def test_api_crear_evento_invalido(auth_client):
    """Prueba que la API rechace la creación con datos inválidos (400 Bad Request)."""
    # Título muy corto y capacidad inválida
    datos_evento = {
        "titulo": "Hi",
        "fecha": "2026-10-10",
        "hora": "10:30",
        "capacidad": -5,
        "tipo_evento": "otro",
        "prioridad": "media",
        "recordatorio": False
    }
    
    response = auth_client.post(
        '/api/eventos',
        data=json.dumps(datos_evento),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    res_data = json.loads(response.data)
    assert res_data['status'] == 'error'
    assert 'errores' in res_data['data']
    errores = res_data['data']['errores']
    assert any("El título debe tener al menos 3 caracteres." in err for err in errores)
    assert any("La capacidad debe ser al menos 1 persona." in err for err in errores)


def test_api_obtener_todos_los_eventos(auth_client):
    """Prueba que GET /api/eventos devuelva todos los eventos insertados."""
    # 1. Crear dos eventos en la base de datos de test
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    evento1 = {
        "titulo": "Evento Integrado Uno",
        "fecha": fecha_futura,
        "hora": "09:00",
        "capacidad": 5
    }
    evento2 = {
        "titulo": "Evento Integrado Dos",
        "fecha": fecha_futura,
        "hora": "16:00",
        "capacidad": 10
    }
    
    auth_client.post('/api/eventos', data=json.dumps(evento1), content_type='application/json')
    auth_client.post('/api/eventos', data=json.dumps(evento2), content_type='application/json')
    
    # 2. Obtener lista
    response = auth_client.get('/api/eventos')
    assert response.status_code == 200
    res_data = json.loads(response.data)
    
    assert res_data['status'] == 'success'
    assert len(res_data['data']['eventos']) >= 2
    titulos = [e['titulo'] for e in res_data['data']['eventos']]
    assert "Evento Integrado Uno" in titulos
    assert "Evento Integrado Dos" in titulos


def test_api_obtener_evento_por_id(auth_client):
    """Prueba GET /api/eventos/<id> para un evento existente e inexistente."""
    # 1. Crear evento
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    evento = {
        "titulo": "Evento Individual Test",
        "fecha": fecha_futura,
        "hora": "15:00",
        "capacidad": 3
    }
    create_resp = auth_client.post('/api/eventos', data=json.dumps(evento), content_type='application/json')
    nuevo_id = json.loads(create_resp.data)['data']['id']
    
    # 2. Consultar ID existente
    response = auth_client.get(f'/api/eventos/{nuevo_id}')
    assert response.status_code == 200
    res_data = json.loads(response.data)
    assert res_data['status'] == 'success'
    assert res_data['data']['titulo'] == "Evento Individual Test"
    
    # 3. Consultar ID inexistente
    response_404 = auth_client.get('/api/eventos/99999')
    assert response_404.status_code == 404
    res_404_data = json.loads(response_404.data)
    assert res_404_data['status'] == 'error'
    assert "No se encontró un evento" in res_404_data['message']


def test_api_actualizar_evento(auth_client):
    """Prueba PUT /api/eventos/<id> para modificar un evento existente."""
    # 1. Crear evento
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    evento = {
        "titulo": "Evento Original",
        "fecha": fecha_futura,
        "hora": "12:00",
        "capacidad": 1,
        "ubicacion": "Oficina A"
    }
    create_resp = auth_client.post('/api/eventos', data=json.dumps(evento), content_type='application/json')
    nuevo_id = json.loads(create_resp.data)['data']['id']
    
    # 2. Modificar evento
    datos_actualizados = {
        "titulo": "Evento Completamente Modificado",
        "fecha": fecha_futura,
        "hora": "13:00",
        "capacidad": 4,
        "ubicacion": "Oficina B (Remodelada)",
        "tipo_evento": "taller",
        "prioridad": "alta",
        "recordatorio": False
    }
    
    response = auth_client.put(
        f'/api/eventos/{nuevo_id}',
        data=json.dumps(datos_actualizados),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    res_data = json.loads(response.data)
    assert res_data['status'] == 'success'
    assert res_data['data']['titulo'] == "Evento Completamente Modificado"
    assert res_data['data']['capacidad'] == 4
    assert res_data['data']['ubicacion'] == "Oficina B (Remodelada)"


def test_api_eliminar_evento(auth_client):
    """Prueba DELETE /api/eventos/<id>."""
    # 1. Crear evento
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    evento = {
        "titulo": "Evento a Eliminar",
        "fecha": fecha_futura,
        "hora": "12:00",
        "capacidad": 1
    }
    create_resp = auth_client.post('/api/eventos', data=json.dumps(evento), content_type='application/json')
    nuevo_id = json.loads(create_resp.data)['data']['id']
    
    # 2. Eliminar evento
    delete_resp = auth_client.delete(f'/api/eventos/{nuevo_id}')
    assert delete_resp.status_code == 200
    res_delete = json.loads(delete_resp.data)
    assert res_delete['status'] == 'success'
    assert f"Evento con ID {nuevo_id} eliminado exitosamente." in res_delete['message']
    
    # 3. Verificar que ya no exista
    get_resp = auth_client.get(f'/api/eventos/{nuevo_id}')
    assert get_resp.status_code == 404
