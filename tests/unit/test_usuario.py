# ============================================================================
# ARCHIVO: tests/unit/test_usuario.py
# PROPÓSITO: Pruebas unitarias para el modelo de negocio Usuario.
# ============================================================================

import pytest
from models.usuario import Usuario

def test_usuario_valido():
    """Prueba que un usuario con datos correctos pase las validaciones."""
    usuario = Usuario(
        nombre="Juan Pérez",
        email="juan.perez@example.com",
        password="securePassword123"
    )
    errores = usuario.validar()
    assert len(errores) == 0, f"Se esperaban 0 errores, se obtuvieron: {errores}"


def test_usuario_nombre_invalido():
    """Prueba las reglas de validación para el nombre del usuario."""
    # 1. Nombre vacío
    usuario = Usuario(nombre="", email="test@example.com", password="password123")
    errores = usuario.validar()
    assert "El nombre es obligatorio y debe ser texto." in errores

    # 2. Nombre muy corto
    usuario2 = Usuario(nombre="Jo", email="test@example.com", password="password123")
    errores2 = usuario2.validar()
    assert "El nombre debe tener entre 3 y 100 caracteres." in errores2


def test_usuario_email_invalido():
    """Prueba las reglas de validación para el correo electrónico."""
    # 1. Email vacío
    usuario = Usuario(nombre="Test User", email="", password="password123")
    errores = usuario.validar()
    assert "El correo electrónico es obligatorio." in errores

    # 2. Email con formato inválido
    usuario2 = Usuario(nombre="Test User", email="correo-invalido", password="password123")
    errores2 = usuario2.validar()
    assert "El formato del correo electrónico es inválido." in errores2

    usuario3 = Usuario(nombre="Test User", email="correo@sin-punto", password="password123")
    errores3 = usuario3.validar()
    assert "El formato del correo electrónico es inválido." in errores3


def test_usuario_password_invalida():
    """Prueba las reglas de validación para la contraseña en texto plano."""
    # 1. Contraseña vacía (para usuarios nuevos)
    usuario = Usuario(nombre="Test User", email="test@example.com", password="")
    errores = usuario.validar()
    assert "La contraseña es obligatoria para nuevos usuarios." in errores

    # 2. Contraseña muy corta (mínimo 6 caracteres por seguridad)
    usuario2 = Usuario(nombre="Test User", email="test@example.com", password="123")
    errores2 = usuario2.validar()
    assert "La contraseña debe tener al menos 6 caracteres por seguridad." in errores2


def test_usuario_criptografia_password():
    """Prueba el hash seguro y la verificación de contraseñas con Werkzeug."""
    usuario = Usuario(
        nombre="Admin Agendify",
        email="admin@agendify.com",
        password="MySecretPassword123"
    )
    
    # 1. El hash no debe estar vacío y debe ser diferente de la contraseña en texto plano
    assert usuario.password_hash is not None
    assert usuario.password_hash != "MySecretPassword123"
    assert usuario.password_hash.startswith("scrypt:") or usuario.password_hash.startswith("pbkdf2:")

    # 2. Verificar correspondencia correcta
    assert usuario.verificar_password("MySecretPassword123") is True
    assert usuario.verificar_password("WrongPassword") is False


def test_usuario_to_dict():
    """Prueba la serialización del modelo Usuario a diccionario (sin exponer el hash)."""
    usuario = Usuario(
        nombre="Clara Smith",
        email="clara@example.com",
        password="password123",
        id=9
    )
    
    d = usuario.to_dict()
    assert d['id'] == 9
    assert d['nombre'] == "Clara Smith"
    assert d['email'] == "clara@example.com"
    # IMPORTANTE: El diccionario serializado para API jamás debe exponer contraseñas
    assert 'password' not in d
    assert 'password_hash' not in d


def test_usuario_desde_dict():
    """Prueba la creación de un modelo Usuario a partir de datos de BD."""
    data = {
        'id': 100,
        'nombre': 'Roberto Gómez',
        'email': 'roberto@example.com',
        'password_hash': 'scrypt:32768:8:1$randomhashstring'
    }
    
    usuario = Usuario.desde_dict(data)
    assert usuario.id == 100
    assert usuario.nombre == "Roberto Gómez"
    assert usuario.email == "roberto@example.com"
    assert usuario.password_hash == "scrypt:32768:8:1$randomhashstring"
