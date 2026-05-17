# ============================================================================
# ARCHIVO: tests/integration/test_web_routes.py
# PROPÓSITO: Pruebas de integración para las páginas web (vistas) de Agendify.
# ============================================================================

import pytest

def test_web_index_route(client):
    """Prueba que la ruta principal sirve correctamente el index.html de la SPA."""
    response = client.get('/')
    assert response.status_code == 200
    
    # Decodificar el HTML de respuesta
    html_content = response.data.decode('utf-8')
    
    # Verificar elementos estructurales claves definidos en index.html
    assert "<html" in html_content
    assert "<title>Agendify | Precisión Ejecutiva</title>" in html_content
    assert '<div id="app">' in html_content
    
    # Verificar la carga de los recursos JS estáticos de la SPA
    assert 'static/js/main.js' in html_content
    assert 'cdn.tailwindcss.com' in html_content
