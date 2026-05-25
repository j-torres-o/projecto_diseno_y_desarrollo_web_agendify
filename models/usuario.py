# ============================================================================
# ARCHIVO: models/usuario.py
# PROPÓSITO: Modelo de datos para gestionar usuarios y autenticación segura.
#
# La clase Usuario hereda de EntidadBase, lo que le permite reutilizar la
# lógica CRUD base del sistema, implementando además:
#   1. Almacenamiento seguro de contraseñas mediante hashing (scrypt/pbkdf2).
#   2. Validaciones estrictas de datos en el backend (nombre, formato de correo).
#   3. Prevención de inyección SQL mediante el uso de consultas parametrizadas.
#
# NOTA DE SEGURIDAD:
# Nunca debemos almacenar contraseñas en texto plano en la base de datos.
# Agendify utiliza `werkzeug.security` para transformar la contraseña en un
# hash criptográfico irreversible de sentido único.
# ============================================================================

from database import Database
from models.entidad_base import EntidadBase
import re
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(EntidadBase):
    """
    Modelo de datos para usuarios del sistema Agendify.

    Representa las credenciales y perfiles de los usuarios habilitados para
    interactuar con la plataforma, protegiendo las operaciones CRUD.

    Atributos heredados:
        id (int): Identificador único del usuario (Primary Key).
        created_at (str): Fecha de registro del usuario.
        updated_at (str): Fecha de última modificación del usuario.

    Atributos propios:
        nombre (str): Nombre completo del usuario.
        email (str): Correo electrónico (único en la base de datos).
        password (str, opcional): Contraseña en texto plano (solo para validaciones iniciales).
        password_hash (str): Hash criptográfico seguro de la contraseña.
    """

    # Nombre de la tabla asignada en MySQL para este modelo
    TABLA = 'usuarios'

    def __init__(self, nombre, email, password=None, password_hash=None, es_admin=0, activo=1, id=None, created_at=None, updated_at=None):
        """
        Constructor de la clase Usuario.

        Inicializa los atributos básicos heredando de EntidadBase y calcula el hash
        de la contraseña si se proporciona una clave en texto plano.

        Args:
            nombre (str): Nombre completo.
            email (str): Correo electrónico único.
            password (str, opcional): Contraseña en texto plano para nuevos registros.
            password_hash (str, opcional): Hash existente en BD para sesiones o cargas.
            es_admin (int, opcional): Flag de administrador. Default: 0.
            activo (int, opcional): Flag de activo. Default: 1.
            id (int, opcional): ID del registro.
            created_at (str, opcional): Timestamp de creación.
            updated_at (str, opcional): Timestamp de actualización.
        """
        # Invocamos el constructor de EntidadBase
        super().__init__(id, created_at, updated_at)
        
        # Sanitizamos y asignamos los atributos del usuario
        self.nombre = nombre.strip() if nombre else ""
        self.email = email.strip().lower() if email else ""
        self.password = password
        self.es_admin = int(es_admin) if es_admin is not None else 0
        self.activo = int(activo) if activo is not None else 1
        
        # Si se pasa password en texto plano y no hay un hash previo, se encripta
        # de forma segura e irreversible inmediatamente.
        self.password_hash = password_hash or (generate_password_hash(password) if password else None)

    @classmethod
    def desde_dict(cls, datos):
        """
        Factory Method: Crea una instancia de Usuario desde un diccionario.

        Muy útil para inicializar modelos a partir de cuerpos JSON recibidos
        en peticiones HTTP POST/PUT.

        Args:
            datos (dict): Diccionario de datos del usuario.

        Returns:
            Usuario: Instancia configurada del modelo.
        """
        if not datos:
            return None
        return cls(
            id=datos.get('id'),
            nombre=datos.get('nombre'),
            email=datos.get('email'),
            password=datos.get('password'),
            password_hash=datos.get('password_hash'),
            es_admin=datos.get('es_admin', 0),
            activo=datos.get('activo', 1),
            created_at=datos.get('created_at'),
            updated_at=datos.get('updated_at')
        )

    def to_dict(self):
        """
        Serializa la instancia a un diccionario serializable para respuestas JSON.

        NOTA DE SEGURIDAD:
        Por motivos de seguridad, NUNCA debemos incluir campos delicados
        como 'password' o 'password_hash' en respuestas enviadas al frontend.

        Returns:
            dict: Representación segura del usuario.
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'es_admin': bool(self.es_admin),
            'activo': bool(self.activo),
            'created_at': str(self.created_at) if self.created_at else None,
            'updated_at': str(self.updated_at) if self.updated_at else None
        }

    def validar(self):
        """
        Valida que los datos del usuario cumplan con las reglas del negocio.

        Asegura que el nombre sea coherente, el email tenga el formato correcto y
        las nuevas cuentas posean una contraseña lo suficientemente fuerte.

        Returns:
            list[str]: Lista con los mensajes de error. Vacía significa que es válido.
        """
        errores = []

        # --- Validación del Nombre ---
        if not self.nombre or not isinstance(self.nombre, str):
            errores.append("El nombre es obligatorio y debe ser texto.")
        elif len(self.nombre) < 3 or len(self.nombre) > 100:
            errores.append("El nombre debe tener entre 3 y 100 caracteres.")

        # --- Validación del Correo Electrónico ---
        if not self.email or not isinstance(self.email, str):
            errores.append("El correo electrónico es obligatorio.")
        elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.email):
            errores.append("El formato del correo electrónico es inválido.")
        elif len(self.email) > 150:
            errores.append("El correo electrónico no puede exceder 150 caracteres.")

        # --- Validación de la Contraseña ---
        # Solo obligamos a validar 'password' si es un registro nuevo (sin ID).
        if not self.id and not self.password:
            errores.append("La contraseña es obligatoria para nuevos usuarios.")
        elif self.password and len(self.password) < 6:
            errores.append("La contraseña debe tener al menos 6 caracteres por seguridad.")

        return errores

    def verificar_password(self, password):
        """
        Valida si una contraseña ingresada coincide con el hash almacenado en la BD.

        Compara de forma segura (mitigando ataques de temporización o timing attacks)
        las claves.

        Args:
            password (str): La contraseña en texto plano a verificar.

        Returns:
            bool: True si la contraseña es correcta, False de lo contrario.
        """
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def _get_campos_valores(self):
        """
        Retorna las columnas y valores para las consultas generadas por EntidadBase.

        Reemplaza la lógica base para mapear de forma ordenada los atributos
        del modelo a las columnas físicas de MySQL.

        Returns:
            tuple: (lista_de_columnas, lista_de_valores)
        """
        if self.password and not self.password_hash:
            self.password_hash = generate_password_hash(self.password)
        campos = ['nombre', 'email', 'password_hash', 'es_admin', 'activo']
        valores = [self.nombre, self.email, self.password_hash, self.es_admin, self.activo]
        return campos, valores

    @classmethod
    def obtener_por_email(cls, email):
        """
        Consulta un usuario único por su dirección de correo electrónico.

        Utiliza consultas parametrizadas para evitar ataques de Inyección SQL.

        Args:
            email (str): Correo electrónico a buscar.

        Returns:
            Usuario | None: Instancia del usuario si se encuentra, de lo contrario None.
        """
        query = f"SELECT * FROM {cls.TABLA} WHERE email = %s"
        resultado = Database.execute_query(query, (email.strip().lower(),), fetch_one=True)
        return cls.desde_dict(resultado) if resultado else None

    @classmethod
    def obtener_todos(cls):
        """
        Sobrescribe obtener_todos para ordenar los usuarios de forma segura por ID.
        """
        query = "SELECT * FROM usuarios ORDER BY id ASC"
        resultado = Database.execute_query(query, fetch_all=True)
        return resultado if resultado else []

