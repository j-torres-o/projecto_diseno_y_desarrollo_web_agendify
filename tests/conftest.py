# ============================================================================
# ARCHIVO: tests/conftest.py
# PROPÓSITO: Configuración global de pytest y fixtures de testing.
# ============================================================================

import os
import sys
import pytest

# 1. Configurar variables de entorno para pruebas ANTES de cualquier importación.
os.environ['DB_NAME'] = 'agendify_test'
os.environ['TESTING'] = 'True'

# Añadir el directorio raíz al PATH para poder importar los módulos del proyecto.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from app import create_app
import mysql.connector

# Fixture de sesión para configurar y verificar la base de datos de pruebas.
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Fixture que se ejecuta una sola vez al inicio de toda la suite de pruebas.
    Garantiza que la base de datos de pruebas 'agendify_test' exista y tenga la estructura correcta.
    """
    from config import Config
    
    # 1. Intentar conectar al servidor MySQL (sin seleccionar base de datos inicialmente)
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
    except mysql.connector.Error as e:
        pytest.exit(
            f"\n❌ [ERROR CRÍTICO DE ENTORNO]: No se pudo conectar al servidor MySQL en {Config.DB_HOST}:{Config.DB_PORT}.\n"
            f"Por favor, asegúrate de que el servicio MySQL (e.g. MySQL80) esté iniciado.\n"
            f"Error original: {e}"
        )
    
    # 2. Crear la base de datos de prueba si no existe
    try:
        cursor = conn.cursor()
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS agendify_test "
            "CHARACTER SET utf8mb4 "
            "COLLATE utf8mb4_unicode_ci;"
        )
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        pytest.exit(
            f"\n❌ [ERROR DE PERMISOS]: No se pudo crear la base de datos 'agendify_test'.\n"
            f"Asegúrate de que el usuario '{Config.DB_USER}' tiene privilegios suficientes.\n"
            f"Error original: {e}"
        )

    # 3. Crear las tablas a partir del archivo schema.sql en la base de datos agendify_test
    try:
        # Volvemos a conectar, esta vez directamente a la base de datos de prueba
        conn_test = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database='agendify_test'
        )
        cursor_test = conn_test.cursor()
        
        # Leer schema.sql desde la raíz del proyecto
        schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../schema.sql'))
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        # Ejecutar sentencias. Filtramos y ejecutamos solo la creación de tablas eventos.
        # Esto evita re-crear la base de datos agendify de producción/desarrollo descrita en el schema.sql.
        # Buscamos la sentencia CREATE TABLE.
        create_table_sql = ""
        in_create_table = False
        
        for line in schema_sql.splitlines():
            if "CREATE TABLE IF NOT EXISTS eventos" in line or "CREATE TABLE eventos" in line:
                in_create_table = True
            if in_create_table:
                create_table_sql += line + "\n"
                if ") ENGINE=InnoDB;" in line:
                    break
        
        if create_table_sql:
            # Primero eliminamos la tabla existente para comenzar con un esquema limpio
            cursor_test.execute("DROP TABLE IF EXISTS eventos;")
            cursor_test.execute(create_table_sql)
            conn_test.commit()
            print("\nTabla 'eventos' creada exitosamente en base de datos 'agendify_test'.")
        else:
            pytest.exit("❌ No se pudo extraer la definición de la tabla 'eventos' de schema.sql.")
            
        cursor_test.close()
        conn_test.close()
        
    except Exception as e:
        pytest.exit(
            f"\n❌ [ERROR DE INICIALIZACIÓN]: Error al estructurar la base de datos 'agendify_test'.\n"
            f"Error original: {e}"
        )

# Fixture de función para limpiar los datos entre cada prueba individual
@pytest.fixture(autouse=True)
def clean_db():
    """
    Limpia (vacía) la tabla de eventos antes de ejecutar cada prueba individual.
    Garantiza el aislamiento total de los datos en las pruebas de integración.
    """
    # Permitimos continuar sin limpiar si se trata de una prueba puramente unitaria (mockeada)
    try:
        Database.execute_query("DELETE FROM eventos;")
    except mysql.connector.Error:
        # Si falla porque la BD no está configurada o mockeada, se ignora en unitarios
        pass

# Fixture para proveer un cliente de pruebas de la aplicación Flask
@pytest.fixture
def client():
    """
    Retorna un cliente de pruebas de Flask configurado para simular peticiones HTTP.
    """
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
