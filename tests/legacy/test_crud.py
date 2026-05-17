from models.evento import Evento
from database import Database

print("--- TESTING CRUD ---")
try:
    # 1. CREATE
    print("Test CREATE...")
    evento = Evento(titulo="Test Event", fecha="2026-10-10", hora="14:00", capacidad=5)
    nuevo_id = evento.guardar()
    print(f"Creado con ID: {nuevo_id}")

    # 2. READ
    print("Test READ...")
    e = Evento.obtener_por_id(nuevo_id)
    print(f"Leido: {e['titulo']} a las {e['hora']}")

    # 3. UPDATE
    print("Test UPDATE...")
    e_obj = Evento.desde_dict(e)
    e_obj.titulo = "Test Event Modificado"
    e_obj.actualizar()
    e2 = Evento.obtener_por_id(nuevo_id)
    print(f"Modificado: {e2['titulo']}")

    # 4. DELETE
    print("Test DELETE...")
    Evento.eliminar(nuevo_id)
    e3 = Evento.obtener_por_id(nuevo_id)
    print(f"Existe despues de delete? {e3 is not None}")

    print("ALL TESTS PASSED")
except Exception as e:
    print(f"ERROR: {e}")
