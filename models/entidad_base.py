# ============================================================================
# ARCHIVO: models/entidad_base.py
# PROPÓSITO: Clase base abstracta para todas las entidades del sistema.
#
# Esta clase implementa el concepto de HERENCIA. En POO, una clase padre
# (o "superclase") define atributos y métodos comunes que serán compartidos
# por todas las clases hijas (o "subclases").
#
# Ventajas de este enfoque:
#   1. Reutilización de código: No repetimos la lógica de CRUD en cada entidad.
#   2. Consistencia: Todas las entidades siguen el mismo patrón de operaciones.
#   3. Mantenibilidad: Si cambiamos la lógica de conexión, solo lo hacemos aquí.
#
# Esta clase es "abstracta" porque NO debe instanciarse directamente.
# Solo existe para ser heredada por clases concretas como Evento.
# ============================================================================

from database import Database
from mysql.connector import Error as MySQLError


class EntidadBase:
    """
    Clase base abstracta que define la interfaz común para todas las
    entidades persistentes del sistema Agendify.

    Implementa el patrón Template Method: define la estructura de las
    operaciones CRUD, pero delega los detalles específicos (como el nombre
    de la tabla o los campos) a las clases hijas.

    Atributos:
        TABLA (str): Nombre de la tabla en la BD. Debe ser definido
            por cada clase hija.
        id (int): Identificador único del registro.
        created_at (str): Fecha y hora de creación del registro.
        updated_at (str): Fecha y hora de la última actualización.
    """

    # Cada clase hija debe sobrescribir este atributo con el nombre
    # de su tabla correspondiente en la base de datos.
    TABLA = None

    def __init__(self, id=None, created_at=None, updated_at=None):
        """
        Constructor de la clase base.

        Args:
            id (int, optional): ID del registro. None para registros nuevos.
            created_at (str, optional): Timestamp de creación.
            updated_at (str, optional): Timestamp de última modificación.
        """
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at

    def validar(self):
        """
        Método plantilla para validación de datos.

        Las clases hijas DEBEN sobrescribir este método con su lógica
        de validación específica. Si no lo hacen, se lanzará un error.

        Returns:
            list: Lista de strings con mensajes de error. Lista vacía = válido.

        Raises:
            NotImplementedError: Si la clase hija no implementa este método.
        """
        raise NotImplementedError(
            f"La clase {self.__class__.__name__} debe implementar el método validar()."
        )

    def _get_campos_valores(self):
        """
        Método protegido que las clases hijas deben implementar.

        Retorna los nombres de columnas y sus valores correspondientes
        para operaciones INSERT y UPDATE.

        Returns:
            tuple: (lista_de_campos, lista_de_valores)

        Raises:
            NotImplementedError: Si la clase hija no implementa este método.
        """
        raise NotImplementedError(
            f"La clase {self.__class__.__name__} debe implementar _get_campos_valores()."
        )

    def guardar(self):
        """
        Inserta un nuevo registro en la base de datos (operación CREATE).

        Construye dinámicamente la consulta INSERT a partir de los campos
        y valores proporcionados por la clase hija mediante _get_campos_valores().

        NOTA DE SEGURIDAD:
        Se utilizan queries parametrizadas (%s) en lugar de concatenación
        de strings para prevenir ataques de Inyección SQL.

        Returns:
            int: El ID del registro recién insertado.

        Raises:
            ValueError: Si la validación de datos falla.
            MySQLError: Si ocurre un error en la base de datos.
        """
        # Primero validamos los datos antes de intentar guardar.
        errores = self.validar()
        if errores:
            raise ValueError(f"Errores de validación: {'; '.join(errores)}")

        campos, valores = self._get_campos_valores()

        # Construimos la consulta INSERT de forma dinámica:
        # INSERT INTO eventos (titulo, fecha, ...) VALUES (%s, %s, ...)
        placeholders = ', '.join(['%s'] * len(campos))
        nombres_campos = ', '.join(campos)

        query = f"INSERT INTO {self.TABLA} ({nombres_campos}) VALUES ({placeholders})"

        nuevo_id = Database.execute_query(query, tuple(valores))
        self.id = nuevo_id
        return nuevo_id

    def actualizar(self):
        """
        Actualiza un registro existente en la base de datos (operación UPDATE).

        Construye dinámicamente la consulta UPDATE a partir de los campos
        y valores proporcionados por la clase hija.

        Returns:
            int: Número de filas afectadas (debería ser 1).

        Raises:
            ValueError: Si no hay ID o la validación falla.
            MySQLError: Si ocurre un error en la base de datos.
        """
        if not self.id:
            raise ValueError("No se puede actualizar un registro sin ID.")

        errores = self.validar()
        if errores:
            raise ValueError(f"Errores de validación: {'; '.join(errores)}")

        campos, valores = self._get_campos_valores()

        # Construimos: UPDATE eventos SET titulo = %s, fecha = %s, ... WHERE id = %s
        set_clause = ', '.join([f"{campo} = %s" for campo in campos])
        query = f"UPDATE {self.TABLA} SET {set_clause} WHERE id = %s"

        # Añadimos el ID al final de los valores para el WHERE.
        valores.append(self.id)
        return Database.execute_query(query, tuple(valores))

    @classmethod
    def eliminar(cls, id):
        """
        Elimina un registro de la base de datos por su ID (operación DELETE).

        Este es un método de clase (@classmethod) porque no necesitamos
        una instancia del objeto para eliminar — solo el ID.

        Args:
            id (int): El ID del registro a eliminar.

        Returns:
            int: Número de filas eliminadas (debería ser 1).

        Raises:
            MySQLError: Si ocurre un error en la base de datos.
        """
        query = f"DELETE FROM {cls.TABLA} WHERE id = %s"
        return Database.execute_query(query, (id,))

    @classmethod
    def obtener_todos(cls):
        """
        Obtiene todos los registros de la tabla (operación READ - SELECT *).

        Returns:
            list[dict]: Lista de diccionarios, donde cada dict representa
                un registro con sus columnas como claves.
                Ejemplo: [{'id': 1, 'titulo': 'Reunión', ...}, ...]

        Raises:
            MySQLError: Si ocurre un error en la base de datos.
        """
        query = f"SELECT * FROM {cls.TABLA} ORDER BY fecha ASC, hora ASC"
        resultado = Database.execute_query(query, fetch_all=True)
        return resultado if resultado else []

    @classmethod
    def obtener_por_id(cls, id):
        """
        Obtiene un registro específico por su ID (operación READ - SELECT WHERE).

        Args:
            id (int): El ID del registro a buscar.

        Returns:
            dict | None: Diccionario con los datos del registro, o None si
                no se encontró.

        Raises:
            MySQLError: Si ocurre un error en la base de datos.
        """
        query = f"SELECT * FROM {cls.TABLA} WHERE id = %s"
        return Database.execute_query(query, (id,), fetch_one=True)
