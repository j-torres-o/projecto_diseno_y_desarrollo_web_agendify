# ============================================================================
# ARCHIVO: app.py
# PROPÓSITO: Punto de entrada principal de la aplicación Agendify.
#
# En Flask, el patrón "App Factory" consiste en crear la aplicación dentro
# de una función (create_app). Esto tiene varias ventajas:
#   1. Permite crear múltiples instancias (útil para testing).
#   2. Centraliza la configuración en un solo punto.
#   3. Facilita la extensión con Blueprints y extensiones.
#
# ARQUITECTURA MVC:
# - MODELO (Model): Carpeta 'models/' → Clases EntidadBase y Evento.
# - VISTA (View): Carpeta 'templates/' y 'static/' → HTML, CSS, JavaScript.
# - CONTROLADOR (Controller): Carpeta 'routes/' → Blueprints de Flask.
#
# El archivo app.py actúa como el "orquestador" que conecta las 3 capas.
# ============================================================================

from flask import Flask
from config import Config


def create_app():
    """
    Factory Function que crea y configura la aplicación Flask.

    Esta función:
    1. Crea una nueva instancia de Flask.
    2. Carga la configuración desde config.py.
    3. Registra los Blueprints (grupos de rutas).
    4. Configura los manejadores de errores globales.

    Returns:
        Flask: La aplicación Flask configurada y lista para ejecutar.
    """
    # Creamos la instancia de Flask.
    # __name__ le dice a Flask dónde buscar las carpetas 'templates' y 'static'.
    app = Flask(__name__)

    # Cargamos la configuración desde nuestra clase Config.
    # Esto establece SECRET_KEY y otros parámetros.
    app.config.from_object(Config)

    # ---- Registro de Blueprints ----
    # Cada Blueprint es un módulo independiente con sus propias rutas.
    # Esto mantiene el código organizado y modular.
    from routes.main_routes import main_bp
    from routes.api_routes import api_bp

    app.register_blueprint(main_bp)   # Rutas de páginas HTML (/)
    app.register_blueprint(api_bp)    # Rutas de la API (/api/...)

    # ---- Manejadores de Error Globales ----
    # Estos capturan errores que no fueron manejados por las rutas individuales
    # y retornan respuestas JSON consistentes.
    @app.errorhandler(404)
    def not_found(error):
        """Maneja rutas que no existen."""
        from flask import jsonify
        return jsonify({
            'status': 'error',
            'data': None,
            'message': 'Recurso no encontrado.'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores internos del servidor."""
        from flask import jsonify
        return jsonify({
            'status': 'error',
            'data': None,
            'message': 'Error interno del servidor.'
        }), 500

    return app


# Punto de entrada de la aplicación.
# El bloque 'if __name__ == "__main__":' asegura que el servidor solo se inicie
# si ejecutamos este archivo directamente (no si lo importamos en otro lado).
if __name__ == '__main__':
    app = create_app()
    # Iniciamos el servidor en modo depuración (debug=True) para ver errores detallados.
    # El puerto por defecto es el 5000.
    app.run(debug=True, port=5000)
