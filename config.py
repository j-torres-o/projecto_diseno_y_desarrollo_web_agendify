# ============================================================================
# ARCHIVO: config.py
# PROPÓSITO: Configuración centralizada de la aplicación.
#
# Este módulo implementa el patrón "12-Factor App" para la configuración.
# En lugar de escribir contraseñas y datos sensibles directamente en el código
# (lo cual sería un grave riesgo de seguridad), los leemos desde un archivo
# externo (.env) que NUNCA se sube al repositorio (ver .gitignore).
#
# La librería 'python-dotenv' se encarga de leer el archivo .env y cargar
# sus valores como variables de entorno del sistema operativo.
# ============================================================================

import os
from dotenv import load_dotenv

# Cargamos las variables definidas en el archivo .env al entorno del proceso.
# Esto debe ejecutarse ANTES de intentar leer cualquier variable con os.getenv().
load_dotenv()


class Config:
    """
    Clase de configuración para la aplicación Flask.

    Centraliza todos los parámetros de configuración en un solo lugar,
    facilitando el mantenimiento y evitando valores "hardcodeados" dispersos
    por el código.

    Atributos:
        SECRET_KEY (str): Clave secreta para firmar cookies de sesión de Flask.
            Es fundamental para la seguridad de la autenticación basada en sesiones.
        DB_HOST (str): Dirección del servidor de base de datos (por defecto: localhost).
        DB_PORT (int): Puerto del servidor MySQL (por defecto: 3306).
        DB_USER (str): Usuario de la base de datos.
        DB_PASSWORD (str): Contraseña del usuario de la base de datos.
        DB_NAME (str): Nombre de la base de datos a utilizar.
    """

    # Flask necesita una clave secreta para manejar sesiones de forma segura.
    # Si no existe en .env, generamos una por defecto (solo para desarrollo).
    SECRET_KEY = os.getenv('SECRET_KEY', 'agendify-dev-secret-key-2026')

    # Parámetros de conexión a la base de datos MySQL.
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'agendify')
