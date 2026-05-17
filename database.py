# ============================================================================
# ARCHIVO: database.py
# PROPÓSITO: Gestión de la conexión a la base de datos MySQL.
#
# Este módulo implementa el patrón "Singleton" para la conexión a la base
# de datos. En lugar de crear una nueva conexión cada vez que necesitamos
# interactuar con la BD (lo cual sería muy lento e ineficiente), mantenemos
# un "pool" (piscina) de conexiones reutilizables.
#
# También implementamos un "Context Manager" (la sentencia 'with') para
# garantizar que las conexiones siempre se devuelvan al pool, incluso si
# ocurre un error durante la operación.
# ============================================================================

import mysql.connector
from mysql.connector import pooling, Error as MySQLError
from config import Config


class Database:
    """
    Gestor de conexión a la base de datos MySQL.

    Utiliza un pool de conexiones para optimizar el rendimiento y un
    context manager para garantizar la liberación de recursos.

    Ejemplo de uso:
        with Database.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM eventos")
            resultados = cursor.fetchall()

    Atributos de clase:
        _pool: Pool de conexiones MySQL (se inicializa una sola vez).
    """

    _pool = None

    @classmethod
    def _init_pool(cls):
        """
        Inicializa el pool de conexiones si aún no existe.

        Un pool de conexiones es como tener varias "líneas telefónicas"
        abiertas al servidor de BD. Cuando alguien necesita hacer una consulta,
        toma una línea disponible y la devuelve al terminar, en vez de
        "instalar una nueva línea" cada vez.

        Raises:
            MySQLError: Si no se puede establecer conexión con el servidor MySQL.
        """
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="agendify_pool",
                    pool_size=5,  # Máximo 5 conexiones simultáneas
                    pool_reset_session=True,
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci',
                    autocommit=False  # Control manual de transacciones
                )
                print(f"Pool de conexiones creado: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
            except MySQLError as e:
                print(f"Error al crear pool de conexiones: {e}")
                raise

    @classmethod
    def get_connection(cls):
        """
        Obtiene una conexión del pool.

        Returns:
            MySQLConnection: Una conexión activa a la base de datos.

        Raises:
            MySQLError: Si el pool no tiene conexiones disponibles.
        """
        cls._init_pool()
        return cls._pool.get_connection()

    @classmethod
    def execute_query(cls, query, params=None, fetch_one=False, fetch_all=False):
        """
        Ejecuta una consulta SQL de forma segura usando queries parametrizadas.

        NOTA DE SEGURIDAD:
        NUNCA se debe construir una consulta SQL concatenando strings:
            ❌ f"SELECT * FROM usuarios WHERE id = {user_id}"
        Esto permite ataques de Inyección SQL. En su lugar, usamos
        placeholders (%s) y pasamos los valores como parámetros separados:
            ✅ "SELECT * FROM usuarios WHERE id = %s", (user_id,)

        Args:
            query (str): La consulta SQL con placeholders %s.
            params (tuple, optional): Los valores para los placeholders.
            fetch_one (bool): Si True, retorna solo un registro.
            fetch_all (bool): Si True, retorna todos los registros.

        Returns:
            dict | list | int: Dependiendo del tipo de consulta:
                - SELECT con fetch_one: dict con el registro o None.
                - SELECT con fetch_all: lista de dicts.
                - INSERT: el ID del registro insertado (lastrowid).
                - UPDATE/DELETE: número de filas afectadas.

        Raises:
            MySQLError: Si la consulta falla por error de sintaxis o conexión.
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            # dictionary=True hace que los resultados sean dicts {columna: valor}
            # en lugar de tuplas, lo cual es mucho más legible.
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if fetch_one:
                resultado = cursor.fetchone()
                return resultado
            elif fetch_all:
                resultado = cursor.fetchall()
                return resultado
            else:
                # Para INSERT, UPDATE, DELETE: confirmamos la transacción.
                connection.commit()
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

        except MySQLError as e:
            # Si algo falla, revertimos cualquier cambio parcial.
            if connection:
                connection.rollback()
            print(f"Error en consulta SQL: {e}")
            print(f"   Query: {query}")
            print(f"   Params: {params}")
            raise

        finally:
            # SIEMPRE cerramos cursor y devolvemos la conexión al pool.
            # El bloque 'finally' se ejecuta sin importar si hubo error o no.
            if cursor:
                cursor.close()
            if connection:
                connection.close()
