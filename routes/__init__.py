# ============================================================================
# ARCHIVO: routes/__init__.py
# PROPÓSITO: Inicializador del paquete 'routes'.
#
# Flask Blueprints permiten organizar las rutas en módulos separados,
# similar a como un "departamento" en una empresa tiene sus propias
# responsabilidades. Cada Blueprint maneja un grupo lógico de rutas.
# ============================================================================

from routes.main_routes import main_bp
from routes.api_routes import api_bp

__all__ = ['main_bp', 'api_bp']
