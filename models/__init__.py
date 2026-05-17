# ============================================================================
# ARCHIVO: models/__init__.py
# PROPÓSITO: Inicializador del paquete 'models'.
#
# En Python, un directorio con un archivo __init__.py se convierte en un
# "paquete". Esto nos permite organizar el código en módulos separados
# e importarlos de forma limpia:
#     from models.evento import Evento
# ============================================================================

from models.entidad_base import EntidadBase
from models.evento import Evento

# __all__ define qué se exporta cuando alguien hace: from models import *
__all__ = ['EntidadBase', 'Evento']
