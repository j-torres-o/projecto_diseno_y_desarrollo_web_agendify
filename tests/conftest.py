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
            
        # 3. Crear las tablas a partir del archivo schema.sql en la base de datos agendify_test
        # Primero eliminamos las tablas existentes para comenzar con un esquema limpio.
        cursor_test.execute("DROP TABLE IF EXISTS invitaciones_evento;")
        cursor_test.execute("DROP TABLE IF EXISTS eventos;")
        cursor_test.execute("DROP TABLE IF EXISTS usuarios;")
        conn_test.commit()

        # Separamos por punto y coma para obtener comandos individuales y ejecutamos las de creación
        statements = schema_sql.split(';')
        tablas_creadas = 0
        for stmt in statements:
            stmt_clean = stmt.strip()
            if "CREATE TABLE" in stmt_clean.upper():
                cursor_test.execute(stmt_clean)
                tablas_creadas += 1
        
        conn_test.commit()
        if tablas_creadas >= 3:
            print(f"\nTablas creadas exitosamente en base de datos 'agendify_test' ({tablas_creadas} tablas).")
        else:
            pytest.exit("❌ No se pudieron recrear las tablas requeridas desde schema.sql.")
            
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
    Limpia (vacía) las tablas de eventos y usuarios antes de ejecutar cada prueba individual.
    Garantiza el aislamiento total de los datos en las pruebas de integración.
    """
    # Permitimos continuar sin limpiar si se trata de una prueba puramente unitaria (mockeada)
    try:
        Database.execute_query("DELETE FROM invitaciones_evento;")
        Database.execute_query("DELETE FROM eventos;")
        Database.execute_query("DELETE FROM usuarios;")
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

# Fixture para crear un usuario de prueba persistente en base de datos
@pytest.fixture
def setup_user():
    """
    Crea, valida y guarda un usuario de prueba en la base de datos de test.
    """
    from models.usuario import Usuario
    # Garantizamos limpiar usuarios duplicados
    try:
        Database.execute_query("DELETE FROM usuarios;")
    except:
        pass
    user = Usuario(nombre="Test User", email="test@agendify.com", password="password123")
    user.guardar()
    return user

# Fixture para proveer un cliente de Flask con una sesión activa ya simulada
@pytest.fixture
def auth_client(client, setup_user):
    """
    Retorna un cliente de pruebas con cookies de sesión ya inicializadas
    con el ID del usuario de pruebas.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = setup_user.id
        sess['user_name'] = setup_user.nombre
    return client
