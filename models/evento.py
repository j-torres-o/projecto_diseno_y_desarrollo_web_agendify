# ============================================================================
# ARCHIVO: models/evento.py
# PROPÓSITO: Modelo de datos para los eventos del calendario Agendify.
#
# La clase Evento HEREDA de EntidadBase. Esto significa que Evento obtiene
# automáticamente todos los atributos y métodos de EntidadBase (id, created_at,
# guardar(), actualizar(), eliminar(), obtener_todos(), obtener_por_id()).
#
# Lo que Evento añade es su lógica ESPECÍFICA:
#   - Sus propios atributos (titulo, fecha, ubicacion, etc.).
#   - Su propia validación de datos (validar()).
#   - Sus propios métodos de serialización (to_dict(), desde_dict()).
#
# La llamada super().__init__() dentro del constructor es fundamental:
# invoca el constructor de la clase padre para inicializar los atributos
# comunes (id, created_at, updated_at).
# ============================================================================

import html
from datetime import date, datetime, time
from models.entidad_base import EntidadBase
from database import Database


class Evento(EntidadBase):
    """
    Modelo de datos para eventos del calendario Agendify.

    Hereda de EntidadBase y añade atributos y validaciones específicas
    para la gestión de eventos. Implementa el CRUD completo mediante
    los métodos heredados y los propios.

    Atributos heredados:
        id (int): Identificador único del evento.
        created_at (str): Fecha de creación del registro.
        updated_at (str): Fecha de última actualización.

    Atributos propios:
        titulo (str): Nombre del evento (3-100 caracteres).
        fecha (str): Fecha del evento en formato 'YYYY-MM-DD'.
        hora (str): Hora de inicio en formato 'HH:MM'.
        ubicacion (str): Lugar físico o enlace virtual.
        descripcion (str): Detalle extendido del evento.
        capacidad (int): Número máximo de asistentes (mínimo 1).
        tipo_evento (str): Categoría del evento (taller/reunion/social/conferencia/otro).
        prioridad (str): Nivel de urgencia (baja/media/alta).
        recordatorio (bool): Si se activa recordatorio.

    Ejemplo de uso:
        evento = Evento(
            titulo="Reunión de Planificación",
            fecha="2026-06-01",
            hora="10:00",
            ubicacion="Sala de Juntas A",
            descripcion="Revisión del primer trimestre",
            capacidad=15,
            tipo_evento="reunion",
            prioridad="alta",
            recordatorio=True
        )
        errores = evento.validar()
        if not errores:
            evento.guardar()
    """

    # Nombre de la tabla en la base de datos.
    # Esta constante la usa EntidadBase para construir las consultas SQL.
    TABLA = 'eventos'

    # Valores válidos para campos ENUM (deben coincidir con el schema.sql).
    TIPOS_VALIDOS = ['taller', 'reunion', 'social', 'conferencia', 'otro']
    PRIORIDADES_VALIDAS = ['baja', 'media', 'alta']

    def __init__(self, titulo, fecha, hora, creador_id=None, creador_nombre=None, ubicacion='', descripcion='',
                 capacidad=1, tipo_evento='otro', prioridad='media',
                 recordatorio=False, id=None, created_at=None, updated_at=None):
        """
        Constructor de la clase Evento.

        Llama al constructor de la clase padre (super().__init__) para
        inicializar los atributos comunes y luego establece los atributos
        específicos del evento.

        Args:
            titulo (str): Nombre del evento.
            fecha (str): Fecha en formato 'YYYY-MM-DD'.
            hora (str): Hora en formato 'HH:MM' o 'HH:MM:SS'.
            creador_id (int, optional): ID del usuario creador del evento.
            creador_nombre (str, optional): Nombre del usuario creador.
            ubicacion (str, optional): Lugar del evento.
            descripcion (str, optional): Descripción detallada.
            capacidad (int, optional): Número máximo de asistentes. Default: 1.
            tipo_evento (str, optional): Categoría del evento. Default: 'otro'.
            prioridad (str, optional): Nivel de prioridad. Default: 'media'.
            recordatorio (bool, optional): Activar recordatorio. Default: False.
            id (int, optional): ID del registro (para edición).
            created_at (str, optional): Timestamp de creación.
            updated_at (str, optional): Timestamp de actualización.
        """
        # Invocamos el constructor de la clase padre (EntidadBase).
        super().__init__(id, created_at, updated_at)

        # Atributos específicos del evento.
        # strip() elimina espacios en blanco al inicio y final (equivalente
        # a la función trim() de PHP que se vio en clase).
        self.titulo = self._sanitizar(titulo)
        self.fecha = fecha
        self.hora = hora
        self.creador_id = creador_id
        self.creador_nombre = creador_nombre
        self.ubicacion = self._sanitizar(ubicacion) if ubicacion else ''
        self.descripcion = self._sanitizar(descripcion) if descripcion else ''
        self.capacidad = capacidad
        self.tipo_evento = tipo_evento
        self.prioridad = prioridad
        self.recordatorio = recordatorio

    @staticmethod
    def _sanitizar(valor):
        """
        Sanitiza un valor de texto para prevenir ataques XSS.

        NOTA DE SEGURIDAD:
        html.escape() convierte caracteres peligrosos en entidades HTML:
            < → &lt;     > → &gt;     " → &quot;     ' → &#x27;
        Esto evita que un usuario malicioso inyecte código JavaScript
        a través de los campos del formulario.

        Args:
            valor (str): El texto a sanitizar.

        Returns:
            str: El texto sanitizado y sin espacios extra.
        """
        if not isinstance(valor, str):
            return str(valor).strip()
        return html.escape(valor.strip())

    def validar(self):
        """
        Valida todos los campos del evento según las reglas de negocio.

        REGLAS DE VALIDACIÓN:
        1. Título: Obligatorio, entre 3 y 100 caracteres.
        2. Fecha: Obligatoria, no puede ser una fecha pasada.
        3. Hora: Obligatoria, formato válido.
        4. Capacidad: Debe ser un entero mayor a 0.
        5. Tipo de evento: Debe estar en la lista de tipos válidos.
        6. Prioridad: Debe estar en la lista de prioridades válidas.

        Returns:
            list[str]: Lista de mensajes de error. Si está vacía, los
                datos son válidos.
        """
        errores = []

        # --- Validación del título ---
        if not self.titulo or not self.titulo.strip():
            errores.append("El título del evento es obligatorio.")
        elif len(self.titulo) < 3:
            errores.append("El título debe tener al menos 3 caracteres.")
        elif len(self.titulo) > 100:
            errores.append("El título no puede exceder 100 caracteres.")

        # --- Validación de la fecha ---
        if not self.fecha:
            errores.append("La fecha del evento es obligatoria.")
        else:
            try:
                fecha_evento = date.fromisoformat(str(self.fecha))
                if fecha_evento < date.today():
                    errores.append("La fecha del evento no puede ser en el pasado.")
            except (ValueError, TypeError):
                errores.append("Formato de fecha inválido. Use AAAA-MM-DD.")

        # --- Validación de la hora ---
        if not self.hora:
            errores.append("La hora del evento es obligatoria.")
        else:
            try:
                # Intentamos parsear la hora en los formatos comunes.
                hora_str = str(self.hora)
                if len(hora_str) == 5:  # HH:MM
                    time.fromisoformat(hora_str)
                elif len(hora_str) == 8:  # HH:MM:SS
                    time.fromisoformat(hora_str)
                else:
                    errores.append("Formato de hora inválido. Use HH:MM.")
            except (ValueError, TypeError):
                errores.append("Formato de hora inválido. Use HH:MM.")

        # --- Validación de capacidad ---
        try:
            capacidad_int = int(self.capacidad)
            if capacidad_int < 1:
                errores.append("La capacidad debe ser al menos 1 persona.")
            self.capacidad = capacidad_int
        except (ValueError, TypeError):
            errores.append("La capacidad debe ser un número entero válido.")

        # --- Validación de tipo de evento ---
        if self.tipo_evento not in self.TIPOS_VALIDOS:
            errores.append(
                f"Tipo de evento inválido. Opciones válidas: {', '.join(self.TIPOS_VALIDOS)}"
            )

        # --- Validación de prioridad ---
        if self.prioridad not in self.PRIORIDADES_VALIDAS:
            errores.append(
                f"Prioridad inválida. Opciones válidas: {', '.join(self.PRIORIDADES_VALIDAS)}"
            )

        return errores

    def _get_campos_valores(self):
        """
        Retorna los campos y valores del evento para las operaciones SQL.

        Este método es usado internamente por EntidadBase.guardar() y
        EntidadBase.actualizar() para construir las consultas SQL de
        forma dinámica.

        Returns:
            tuple: (lista_de_nombres_de_campo, lista_de_valores)
        """
        campos = [
            'titulo', 'fecha', 'hora', 'creador_id', 'ubicacion', 'descripcion',
            'capacidad', 'tipo_evento', 'prioridad', 'recordatorio'
        ]
        valores = [
            self.titulo,
            str(self.fecha),
            str(self.hora),
            self.creador_id,
            self.ubicacion,
            self.descripcion,
            self.capacidad,
            self.tipo_evento,
            self.prioridad,
            self.recordatorio
        ]
        return campos, valores

    def to_dict(self):
        """
        Serializa el objeto Evento a un diccionario Python.

        Esto es necesario para convertir el objeto a JSON cuando la API
        responde al frontend. json.dumps() no puede serializar objetos
        Python directamente, pero sí puede serializar diccionarios.

        Returns:
            dict: Representación del evento como diccionario.
        """
        return {
            'id': self.id,
            'titulo': self.titulo,
            'fecha': str(self.fecha) if self.fecha else None,
            'hora': str(self.hora) if self.hora else None,
            'creador_id': self.creador_id,
            'creador_nombre': self.creador_nombre,
            'ubicacion': self.ubicacion,
            'descripcion': self.descripcion,
            'capacidad': self.capacidad,
            'tipo_evento': self.tipo_evento,
            'prioridad': self.prioridad,
            'recordatorio': bool(self.recordatorio),
            'created_at': str(self.created_at) if self.created_at else None,
            'updated_at': str(self.updated_at) if self.updated_at else None
        }

    @classmethod
    def desde_dict(cls, data):
        """
        Factory Method: Crea una instancia de Evento desde un diccionario.

        Este patrón es útil para convertir los datos que llegan del
        formulario (como diccionario request.json) directamente en un
        objeto Evento listo para validar y guardar.

        Args:
            data (dict): Diccionario con los datos del evento.
                Claves esperadas: titulo, fecha, hora, ubicacion,
                descripcion, capacidad, tipo_evento, prioridad, recordatorio.

        Returns:
            Evento: Una nueva instancia de Evento.
        """
        return cls(
            titulo=data.get('titulo', ''),
            fecha=data.get('fecha', ''),
            hora=data.get('hora', ''),
            creador_id=data.get('creador_id'),
            creador_nombre=data.get('creador_nombre'),
            ubicacion=data.get('ubicacion', ''),
            descripcion=data.get('descripcion', ''),
            capacidad=data.get('capacidad', 1),
            tipo_evento=data.get('tipo_evento', 'otro'),
            prioridad=data.get('prioridad', 'media'),
            recordatorio=data.get('recordatorio', False),
            id=data.get('id')
        )

    @classmethod
    def obtener_paginados(cls, page=1, limit=10, fecha=None, tipo_evento=None, prioridad=None, creador_id=None):
        """
        Sobrescribe obtener_paginados para incluir el creador_nombre en los eventos y admitir filtros dinámicos.
        """
        offset = (page - 1) * limit
        where_clauses = []
        params = []

        if fecha:
            where_clauses.append("e.fecha = %s")
            params.append(fecha)
        if tipo_evento:
            where_clauses.append("e.tipo_evento = %s")
            params.append(tipo_evento)
        if prioridad:
            where_clauses.append("e.prioridad = %s")
            params.append(prioridad)
        if creador_id:
            where_clauses.append("e.creador_id = %s")
            params.append(creador_id)

        where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        count_query = f"SELECT COUNT(*) as total FROM eventos e {where_str}"
        total_res = Database.execute_query(count_query, tuple(params) if params else None, fetch_one=True)
        total = total_res['total'] if total_res else 0
        
        query = f"""
            SELECT e.*, u.nombre as creador_nombre
            FROM eventos e
            INNER JOIN usuarios u ON e.creador_id = u.id
            {where_str}
            ORDER BY e.fecha ASC, e.hora ASC
            LIMIT %s OFFSET %s
        """
        params_query = params.copy()
        params_query.extend([limit, offset])
        resultado = Database.execute_query(query, tuple(params_query), fetch_all=True)
        return resultado if resultado else [], total

    @classmethod
    def obtener_paginados_por_usuario(cls, usuario_id, page=1, limit=10, fecha=None, tipo_evento=None, prioridad=None, creador_id=None):
        """
        Obtiene de forma paginada y con soporte para filtros dinámicos los eventos creados por el usuario o a los que ha sido invitado.
        """
        offset = (page - 1) * limit
        where_clauses = ["(e.creador_id = %s OR ie.usuario_id = %s)"]
        params = [usuario_id, usuario_id]

        if fecha:
            where_clauses.append("e.fecha = %s")
            params.append(fecha)
        if tipo_evento:
            where_clauses.append("e.tipo_evento = %s")
            params.append(tipo_evento)
        if prioridad:
            where_clauses.append("e.prioridad = %s")
            params.append(prioridad)
        if creador_id:
            where_clauses.append("e.creador_id = %s")
            params.append(creador_id)

        where_str = " WHERE " + " AND ".join(where_clauses)
        
        # 1. CONSULTA DE CONTEO TOTAL:
        count_query = f"""
            SELECT COUNT(DISTINCT e.id) as total 
            FROM eventos e
            LEFT JOIN invitaciones_evento ie ON e.id = ie.evento_id
            {where_str}
        """
        total_resultado = Database.execute_query(count_query, tuple(params), fetch_one=True)
        total = total_resultado['total'] if total_resultado else 0
        
        # 2. CONSULTA DE REGISTROS PAGINADOS:
        query = f"""
            SELECT DISTINCT e.*, u.nombre as creador_nombre 
            FROM eventos e
            INNER JOIN usuarios u ON e.creador_id = u.id
            LEFT JOIN invitaciones_evento ie ON e.id = ie.evento_id
            {where_str}
            ORDER BY e.fecha ASC, e.hora ASC 
            LIMIT %s OFFSET %s
        """
        params_query = params.copy()
        params_query.extend([limit, offset])
        resultado = Database.execute_query(query, tuple(params_query), fetch_all=True)
        return resultado if resultado else [], total

    def agregar_invitado(self, usuario_id):
        """
        Asocia un usuario al evento insertándolo en la tabla invitaciones_evento.

        Args:
            usuario_id (int): El ID del usuario a invitar.
        """
        query = "INSERT IGNORE INTO invitaciones_evento (evento_id, usuario_id) VALUES (%s, %s)"
        Database.execute_query(query, (self.id, usuario_id))

    def eliminar_invitado(self, usuario_id):
        """
        Elimina un usuario de las invitaciones del evento.

        Args:
            usuario_id (int): El ID del usuario a desinvitar.
        """
        query = "DELETE FROM invitaciones_evento WHERE evento_id = %s AND usuario_id = %s"
        Database.execute_query(query, (self.id, usuario_id))

    def obtener_invitados(self):
        """
        Retorna la lista de usuarios invitados a este evento.

        Returns:
            list[dict]: Lista de usuarios invitados.
        """
        query = """
            SELECT u.id, u.nombre, u.email 
            FROM usuarios u
            INNER JOIN invitaciones_evento ie ON u.id = ie.usuario_id
            WHERE ie.evento_id = %s
        """
        resultado = Database.execute_query(query, (self.id,), fetch_all=True)
        return resultado if resultado else []

    @classmethod
    def obtener_por_id(cls, id):
        """
        Sobrescribe obtener_por_id para traer el creador_nombre de forma transparente.
        """
        query = """
            SELECT e.*, u.nombre as creador_nombre
            FROM eventos e
            INNER JOIN usuarios u ON e.creador_id = u.id
            WHERE e.id = %s
        """
        return Database.execute_query(query, (id,), fetch_one=True)


