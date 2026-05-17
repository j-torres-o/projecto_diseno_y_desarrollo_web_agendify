# ============================================================================
# ARCHIVO: tests/unit/test_models.py
# PROPÓSITO: Pruebas unitarias de modelos de Agendify (Evento y EntidadBase).
# ============================================================================

import pytest
from datetime import date, timedelta
from models.evento import Evento
from database import Database

# --- PRUEBAS DE VALIDACIÓN ---

def test_evento_valido():
    """Prueba que un evento con datos correctos pase la validación."""
    fecha_futura = (date.today() + timedelta(days=2)).isoformat()
    evento = Evento(
        titulo="Evento de Prueba Válido",
        fecha=fecha_futura,
        hora="18:30",
        capacidad=10,
        tipo_evento="taller",
        prioridad="media"
    )
    errores = evento.validar()
    assert len(errores) == 0, f"Se esperaban 0 errores, se obtuvieron: {errores}"


def test_evento_titulo_invalido():
    """Prueba las reglas de validación del título del evento."""
    fecha_futura = (date.today() + timedelta(days=2)).isoformat()
    
    # 1. Título vacío
    evento = Evento(titulo="", fecha=fecha_futura, hora="18:30")
    errores = evento.validar()
    assert "El título del evento es obligatorio." in errores

    # 2. Título muy corto
    evento = Evento(titulo="Ab", fecha=fecha_futura, hora="18:30")
    errores = evento.validar()
    assert "El título debe tener al menos 3 caracteres." in errores

    # 3. Título muy largo (> 100)
    titulo_largo = "A" * 101
    evento = Evento(titulo=titulo_largo, fecha=fecha_futura, hora="18:30")
    errores = evento.validar()
    assert "El título no puede exceder 100 caracteres." in errores


def test_evento_fecha_invalida():
    """Prueba las reglas de validación de la fecha del evento."""
    # 1. Fecha vacía
    evento = Evento(titulo="Evento Test", fecha="", hora="18:30")
    errores = evento.validar()
    assert "La fecha del evento es obligatoria." in errores

    # 2. Fecha pasada
    fecha_pasada = (date.today() - timedelta(days=1)).isoformat()
    evento = Evento(titulo="Evento Test", fecha=fecha_pasada, hora="18:30")
    errores = evento.validar()
    assert "La fecha del evento no puede ser en el pasado." in errores

    # 3. Formato incorrecto
    evento = Evento(titulo="Evento Test", fecha="10-10-2026", hora="18:30")
    errores = evento.validar()
    assert "Formato de fecha inválido. Use AAAA-MM-DD." in errores


def test_evento_hora_invalida():
    """Prueba las reglas de validación de la hora del evento."""
    fecha_futura = (date.today() + timedelta(days=2)).isoformat()
    
    # 1. Hora vacía
    evento = Evento(titulo="Evento Test", fecha=fecha_futura, hora="")
    errores = evento.validar()
    assert "La hora del evento es obligatoria." in errores

    # 2. Formato incorrecto
    evento = Evento(titulo="Evento Test", fecha=fecha_futura, hora="18")
    errores = evento.validar()
    assert "Formato de hora inválido. Use HH:MM." in errores

    evento2 = Evento(titulo="Evento Test", fecha=fecha_futura, hora="abc")
    errores2 = evento2.validar()
    assert "Formato de hora inválido. Use HH:MM." in errores2


def test_evento_capacidad_invalida():
    """Prueba las reglas de validación de la capacidad del evento."""
    fecha_futura = (date.today() + timedelta(days=2)).isoformat()
    
    # 1. Capacidad menor a 1
    evento = Evento(titulo="Evento Test", fecha=fecha_futura, hora="18:30", capacidad=0)
    errores = evento.validar()
    assert "La capacidad debe ser al menos 1 persona." in errores

    # 2. Capacidad no numérica
    evento2 = Evento(titulo="Evento Test", fecha=fecha_futura, hora="18:30", capacidad="cinco")
    errores2 = evento2.validar()
    assert "La capacidad debe ser un número entero válido." in errores2


def test_evento_tipo_prioridad_invalidos():
    """Prueba las restricciones ENUM de tipo y prioridad."""
    fecha_futura = (date.today() + timedelta(days=2)).isoformat()
    
    # Tipo inválido
    evento = Evento(titulo="Evento Test", fecha=fecha_futura, hora="18:30", tipo_evento="invalido")
    errores = evento.validar()
    assert any("Tipo de evento inválido" in err for err in errores)

    # Prioridad inválida
    evento2 = Evento(titulo="Evento Test", fecha=fecha_futura, hora="18:30", prioridad="critica")
    errores2 = evento2.validar()
    assert any("Prioridad inválida" in err for err in errores2)


# --- PRUEBAS DE SERIALIZACIÓN ---

def test_evento_to_dict():
    """Prueba la serialización a diccionario."""
    evento = Evento(
        titulo="Evento Test Serializado",
        fecha="2026-11-20",
        hora="10:00",
        ubicacion="Oficina",
        descripcion="Desc",
        capacidad=5,
        tipo_evento="reunion",
        prioridad="baja",
        recordatorio=True,
        id=42
    )
    
    d = evento.to_dict()
    assert d['id'] == 42
    assert d['titulo'] == "Evento Test Serializado"
    assert d['fecha'] == "2026-11-20"
    assert d['hora'] == "10:00"
    assert d['ubicacion'] == "Oficina"
    assert d['descripcion'] == "Desc"
    assert d['capacidad'] == 5
    assert d['tipo_evento'] == "reunion"
    assert d['prioridad'] == "baja"
    assert d['recordatorio'] is True


def test_evento_desde_dict():
    """Prueba la creación de un objeto Evento a partir de un diccionario."""
    data = {
        'id': 99,
        'titulo': 'Evento desde dict',
        'fecha': '2026-12-15',
        'hora': '14:00',
        'ubicacion': 'Virtual',
        'descripcion': 'Llamada Zoom',
        'capacidad': 100,
        'tipo_evento': 'conferencia',
        'prioridad': 'alta',
        'recordatorio': True
    }
    
    evento = Evento.desde_dict(data)
    assert evento.id == 99
    assert evento.titulo == "Evento desde dict"
    assert evento.fecha == "2026-12-15"
    assert evento.hora == "14:00"
    assert evento.ubicacion == "Virtual"
    assert evento.descripcion == "Llamada Zoom"
    assert evento.capacidad == 100
    assert evento.tipo_evento == "conferencia"
    assert evento.prioridad == "alta"
    assert evento.recordatorio is True


# --- PRUEBAS UNITARIAS CON MOCKS ---

def test_guardar_evento_con_mock(mocker):
    """Prueba el método guardar() sin tocar la BD usando pytest-mock."""
    # Parcheamos Database.execute_query para que no intente conectarse a MySQL
    # y devuelva un ID simulado (por ejemplo, 15).
    mock_execute = mocker.patch.object(Database, 'execute_query', return_value=15)
    
    fecha_futura = (date.today() + timedelta(days=2)).isoformat()
    evento = Evento(
        titulo="Evento Mockeado",
        fecha=fecha_futura,
        hora="12:00",
        capacidad=2
    )
    
    nuevo_id = evento.guardar()
    
    assert nuevo_id == 15
    assert evento.id == 15
    # Verificar que execute_query fue llamado correctamente
    mock_execute.assert_called_once()
    args, kwargs = mock_execute.call_args
    assert "INSERT INTO eventos" in args[0]
    assert "Evento Mockeado" in args[1]


def test_actualizar_evento_con_mock(mocker):
    """Prueba el método actualizar() sin tocar la BD usando pytest-mock."""
    mock_execute = mocker.patch.object(Database, 'execute_query', return_value=1)
    
    fecha_futura = (date.today() + timedelta(days=2)).isoformat()
    evento = Evento(
        titulo="Evento a Actualizar",
        fecha=fecha_futura,
        hora="12:00",
        id=88
    )
    
    filas_afectadas = evento.actualizar()
    
    assert filas_afectadas == 1
    mock_execute.assert_called_once()
    args, kwargs = mock_execute.call_args
    assert "UPDATE eventos SET" in args[0]
    assert "Evento a Actualizar" in args[1]
    assert 88 == args[1][-1]  # El ID debe ser el último elemento de la tupla de parámetros
