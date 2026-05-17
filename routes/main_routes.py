# ============================================================================
# ARCHIVO: routes/main_routes.py
# PROPÓSITO: Rutas principales para servir las páginas HTML.
#
# Un Blueprint es como una "mini-aplicación" dentro de Flask. Nos permite
# agrupar rutas relacionadas en un solo módulo. En este caso, agrupamos
# todas las rutas que sirven páginas HTML (la capa de Presentación en MVC).
#
# Los Blueprints se registran en la aplicación principal (app.py) con:
#     app.register_blueprint(main_bp)
# ============================================================================

from flask import Blueprint, render_template

# Creamos un Blueprint llamado 'main'.
# El primer argumento es el nombre interno del blueprint.
# __name__ ayuda a Flask a localizar los recursos del módulo.
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Ruta principal que sirve la aplicación SPA.

    En una Single Page Application (SPA), solo hay una ruta de HTML.
    El JavaScript del frontend se encarga de renderizar las diferentes
    "vistas" (login, dashboard, formularios) dinámicamente.

    Returns:
        str: El contenido HTML renderizado de index.html.
    """
    return render_template('index.html')
