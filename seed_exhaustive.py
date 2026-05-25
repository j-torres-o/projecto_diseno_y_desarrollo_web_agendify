# ============================================================================
# ARCHIVO: seed_exhaustive.py
# PROPÓSITO: Sembrado masivo y exhaustivo de usuarios y eventos para pruebas de estrés.
#
# Uso:
#   venv\Scripts\python seed_exhaustive.py
# ============================================================================

from models.usuario import Usuario
from models.evento import Evento
from database import Database
from datetime import date, timedelta
import random

# Definición de Usuarios de Prueba
USUARIOS_SEMILLA = [
    {"nombre": "Ana Martínez", "email": "ana.martinez@agendify.com", "password": "password123", "es_admin": 0},
    {"nombre": "Carlos Ramírez", "email": "carlos.ramirez@agendify.com", "password": "password123", "es_admin": 0},
    {"nombre": "Sofía Castro", "email": "sofia.castro@agendify.com", "password": "password123", "es_admin": 0},
    {"nombre": "Diego Sánchez", "email": "diego.sanchez@agendify.com", "password": "password123", "es_admin": 0},
    {"nombre": "Lucía Gómez", "email": "lucia.gomez@agendify.com", "password": "password123", "es_admin": 0},
    {"nombre": "Administrador General", "email": "admin@agendify.com", "password": "admin123", "es_admin": 1}
]

# Diccionarios de datos para la generación masiva de eventos
TITULOS_EVENTOS = {
    "taller": [
        "Taller de Introducción a React", "Taller Práctico de CSS Grid y Flexbox",
        "Taller Avanzado de Python", "Taller de Clean Code y Refactorización",
        "Taller de Git & GitHub en Equipos", "Taller de Bases de Datos NoSQL",
        "Taller de Docker para Principiantes", "Taller de UI/UX con Figma"
    ],
    "reunion": [
        "Sincronización Semanal de Proyecto", "Reunión de Planificación Q3",
        "Revisión de Sprint de Desarrollo", "Sesión de Lluvia de Ideas",
        "Reunión de Feedback de Clientes", "Daily Standup de Equipo",
        "Reunión Uno a Uno de Seguimiento", "Comité de Arquitectura Técnica"
    ],
    "social": [
        "Celebración de Cumpleaños de Mayo", "After Office del Equipo",
        "Almuerzo de Bienvenida de Integrantes", "Torneo Interno de Ping Pong",
        "Coffee Break de Integración", "Festejo de Logros de Proyecto",
        "Brindis Fin de Año / Aniversario", "Sesión de Juegos de Mesa"
    ],
    "conferencia": [
        "El Futuro del Desarrollo de Software", "Tendencias en Ciberseguridad 2026",
        "Charla sobre Inteligencia Artificial Aplicada", "Conferencia de Buenas Prácticas Agile",
        "Keynote de Innovación Tecnológica", "Panel de Liderazgo Femenino en Tech",
        "Seminario de Optimización en la Nube", "Foro de Arquitecturas Microservicios"
    ],
    "otro": [
        "Chequeo Médico Ocupacional", "Revisión de Inventario Trimestral",
        "Mantenimiento Programado de Servidores", "Auditoría Interna de Calidad",
        "Instalación de Nuevos Equipos de Oficina", "Prueba de Simulacro de Incendios"
    ]
}

DESC_EVENTOS = {
    "taller": "Sesión interactiva y de aprendizaje práctico enfocada en adquirir habilidades técnicas clave del día a día.",
    "reunion": "Espacio formal para la alineación del equipo, revisión de entregables, KPIs y toma de decisiones clave.",
    "social": "Actividad informal orientada al esparcimiento, cohesión del grupo, diversión y fortalecimiento del clima laboral.",
    "conferencia": "Presentación magistral con expertos de la industria exponiendo visiones estratégicas, tendencias y casos de estudio exitosos.",
    "otro": "Actividades generales y de soporte operativo del negocio que requieren planificación horaria y reserva de espacios."
}

UBICACIONES = [
    "Sala de Juntas A", "Sala de Juntas B", "Sala de Capacitaciones", "Laboratorio de Innovación",
    "Terraza Común", "Plataforma Virtual Zoom", "Plataforma Virtual Microsoft Teams",
    "Auditorio Principal", "Cafetería del Corporativo", "Oficinas Centrales - Piso 3"
]

HORAS = [
    "08:00", "09:00", "09:30", "10:00", "11:00", "12:00", "13:30", 
    "14:00", "15:00", "16:00", "17:00", "18:30"
]

def main():
    print("=========================================================")
    print("   AGENDIFY - INICIANDO SEEDER EXHAUSTIVO DE PRUEBAS     ")
    print("=========================================================\n")
    
    # 1. Resetear Base de Datos usando schema.sql de forma limpia
    print("[1/4] Inicializando base de datos limpia...")
    try:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            sql_commands = f.read().split(';')
        for command in sql_commands:
            if command.strip():
                Database.execute_query(command)
        print("  - Base de datos estructurada desde cero exitosamente.")
    except Exception as e:
        print(f"  - ❌ Error al inicializar esquema: {e}")
        return

    # 2. Sembrar Usuarios
    print("\n[2/4] Creando usuarios y cuenta administrativa...")
    usuarios_creados = []
    
    for u_info in USUARIOS_SEMILLA:
        nuevo_u = Usuario(
            nombre=u_info["nombre"], 
            email=u_info["email"], 
            password=u_info["password"],
            es_admin=u_info["es_admin"],
            activo=1
        )
        nuevo_id = nuevo_u.guardar()
        nuevo_u.id = nuevo_id
        usuarios_creados.append(nuevo_u)
        print(f"  - Creado: '{nuevo_u.nombre}' ({nuevo_u.email}) [Admin: {bool(nuevo_u.es_admin)}]")
            
    print(f"\n-> Fase 2 terminada. Creados {len(usuarios_creados)} usuarios.\n")
    
    # 3. Generación Masiva de Eventos (Entre 15 y 25 por cada usuario para un total de ~100 eventos)
    print("[3/4] Generando eventos personalizados para cada usuario...")
    hoy = date.today()
    eventos_creados = []
    
    for usuario in usuarios_creados:
        # Los administradores no necesitan eventos por defecto, pero les crearemos también
        num_eventos = random.randint(15, 25)
        print(f"  - Creando {num_eventos} eventos para {usuario.nombre}...")
        
        for i in range(1, num_eventos + 1):
            tipo = random.choice(list(TITULOS_EVENTOS.keys()))
            titulo_base = random.choice(TITULOS_EVENTOS[tipo])
            titulo = f"{titulo_base} - {usuario.nombre.split()[0]} ({i})"
            
            dias_a_sumar = random.randint(1, 90)
            fecha_evento = (hoy + timedelta(days=dias_a_sumar)).isoformat()
            
            hora = random.choice(HORAS)
            ubicacion = random.choice(UBICACIONES)
            descripcion = f"{DESC_EVENTOS[tipo]} Evento privado creado por {usuario.nombre} para propósitos de prueba exhaustiva."
            capacidad = random.choice([5, 10, 20, 50, 100])
            prioridad = random.choice(["baja", "media", "alta"])
            recordatorio = random.choice([True, False])
            
            nuevo_ev = Evento(
                titulo=titulo,
                fecha=fecha_evento,
                hora=hora,
                creador_id=usuario.id,
                creador_nombre=usuario.nombre,
                ubicacion=ubicacion,
                descripcion=descripcion,
                capacidad=capacidad,
                tipo_evento=tipo,
                prioridad=prioridad,
                recordatorio=recordatorio
            )
            
            nuevo_ev.guardar()
            eventos_creados.append(nuevo_ev)
            
    print(f"\n-> Fase 3 terminada. Creados {len(eventos_creados)} eventos independientes en total.\n")
    
    # 4. Generación de Invitaciones
    print("[4/4] Estableciendo red cruzada de invitaciones...")
    invitaciones_conteo = 0
    
    # Excluimos al administrador de invitaciones para simular que los eventos son de usuarios de negocio
    usuarios_negocio = [u for u in usuarios_creados if not u.es_admin]
    
    for evento in eventos_creados:
        # Con una probabilidad del 35%, agregamos invitados de negocio a este evento
        if random.random() < 0.35:
            # Seleccionar entre 1 y 3 invitados al azar
            posibles_invitados = [u for u in usuarios_negocio if u.id != evento.creador_id]
            if posibles_invitados:
                cantidad = min(random.randint(1, 3), len(posibles_invitados))
                invitados_seleccionados = random.sample(posibles_invitados, cantidad)
                for invitado in invitados_seleccionados:
                    evento.agregar_invitado(invitado.id)
                    invitaciones_conteo += 1
                    
    print(f"\n-> Fase 4 terminada. Creadas {invitaciones_conteo} invitaciones cruzadas.\n")
    print("=========================================================")
    print("      SEMBRADO COMPLETADO CON ÉXITO                      ")
    print("=========================================================")
    print(f" - Cuentas de negocio listas: 5 (Contraseña: 'password123')")
    print(f" - Cuenta administrativa lista: admin@agendify.com (Contraseña: 'admin123')")
    print(f" - Total de eventos creados: {len(eventos_creados)}")
    print(f" - Total de invitaciones cruzadas creadas: {invitaciones_conteo}")
    print("=========================================================")

if __name__ == "__main__":
    main()
