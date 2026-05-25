# ============================================================================
# ARCHIVO: tests/integration/test_paginacion.py
# PROPÓSITO: Pruebas de integración de la paginación a nivel BD y API REST.
# ============================================================================

import pytest
import json
from datetime import date, timedelta
from models.evento import Evento

def test_paginacion_base_de_datos(auth_client, setup_user):
    """Prueba que el método obtener_paginados de EntidadBase funcione correctamente en BD."""
    # 1. Sembrar 7 eventos de prueba
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    for i in range(1, 8):
        evento = Evento(
            titulo=f"Evento Paginado {i}",
            fecha=fecha_futura,
            hora=f"10:0{i}",
            capacidad=10,
            creador_id=setup_user.id
        )
        evento.guardar()
        
    # 2. Consultar primera página con límite de 3
    eventos_p1, total_p1 = Evento.obtener_paginados(page=1, limit=3)
    assert len(eventos_p1) == 3
    assert total_p1 == 7
    assert eventos_p1[0]['titulo'] == "Evento Paginado 1"
    
    # 3. Consultar segunda página con límite de 3
    eventos_p2, total_p2 = Evento.obtener_paginados(page=2, limit=3)
    assert len(eventos_p2) == 3
    assert total_p2 == 7
    assert eventos_p2[0]['titulo'] == "Evento Paginado 4"
    
    # 4. Consultar tercera página (última, debería traer 1 solo registro)
    eventos_p3, total_p3 = Evento.obtener_paginados(page=3, limit=3)
    assert len(eventos_p3) == 1
    assert total_p3 == 7
    assert eventos_p3[0]['titulo'] == "Evento Paginado 7"


def test_api_paginacion_metadatos(auth_client):
    """Prueba que la API REST devuelva la estructura de paginación correcta."""
    # 1. Sembrar 6 eventos de prueba
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    for i in range(1, 7):
        evento = {
            "titulo": f"Evento API {i}",
            "fecha": fecha_futura,
            "hora": f"11:0{i}",
            "capacidad": 5
        }
        auth_client.post('/api/eventos', data=json.dumps(evento), content_type='application/json')
        
    # 2. Consumir endpoint GET con page=2 y limit=2
    response = auth_client.get('/api/eventos?page=2&limit=2')
    assert response.status_code == 200
    res_data = json.loads(response.data)
    
    # Verificar estructura de respuesta
    assert res_data['status'] == 'success'
    assert 'pagination' in res_data['data']
    
    # Verificar valores de paginación
    pag = res_data['data']['pagination']
    assert pag['page'] == 2
    assert pag['limit'] == 2
    assert pag['total'] == 6
    assert pag['total_pages'] == 3
    
    # Verificar que los elementos devueltos correspondan a la página 2 (índices 3 y 4: Evento API 3 y 4)
    eventos = res_data['data']['eventos']
    assert len(eventos) == 2
    titulos = [e['titulo'] for e in eventos]
    assert "Evento API 3" in titulos
    assert "Evento API 4" in titulos


def test_api_paginacion_limites_y_sanitizacion(auth_client):
    """Prueba que los parámetros de paginación se saniticen y validen en el backend."""
    # 1. Sembrar 3 eventos
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    for i in range(1, 4):
        evento = {
            "titulo": f"Sanitize Event {i}",
            "fecha": fecha_futura,
            "hora": f"12:0{i}",
            "capacidad": 1
        }
        auth_client.post('/api/eventos', data=json.dumps(evento), content_type='application/json')
        
    # Caso A: Parámetros negativos o inválidos (debería reajustarse a valores por defecto)
    response_neg = auth_client.get('/api/eventos?page=-2&limit=-5')
    assert response_neg.status_code == 200
    res_neg = json.loads(response_neg.data)['data']['pagination']
    assert res_neg['page'] == 1
    assert res_neg['limit'] == 10  # Valor por defecto si es inválido o menor a 1
    
    # Caso B: Límite exagerado (debería topar al máximo permitido en backend de 50)
    response_max = auth_client.get('/api/eventos?page=1&limit=100')
    assert response_max.status_code == 200
    res_max = json.loads(response_max.data)['data']['pagination']
    assert res_max['limit'] == 50  # Cap máximo
    
    # Caso C: Parámetros no numéricos (debería recuperarse con valores por defecto)
    response_abc = auth_client.get('/api/eventos?page=abc&limit=xyz')
    assert response_abc.status_code == 200
    res_abc = json.loads(response_abc.data)['data']['pagination']
    assert res_abc['page'] == 1
    assert res_abc['limit'] == 10
