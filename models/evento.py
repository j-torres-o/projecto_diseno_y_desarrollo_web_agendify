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

    def __init__(self, titulo, fecha, hora, ubicacion='', descripcion='',
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
            'titulo', 'fecha', 'hora', 'ubicacion', 'descripcion',
            'capacidad', 'tipo_evento', 'prioridad', 'recordatorio'
        ]
        valores = [
            self.titulo,
            str(self.fecha),
            str(self.hora),
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
            ubicacion=data.get('ubicacion', ''),
            descripcion=data.get('descripcion', ''),
            capacidad=data.get('capacidad', 1),
            tipo_evento=data.get('tipo_evento', 'otro'),
            prioridad=data.get('prioridad', 'media'),
            recordatorio=data.get('recordatorio', False),
            id=data.get('id')
        )
