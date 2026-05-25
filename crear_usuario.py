# ============================================================================
# ARCHIVO: crear_usuario.py
# PROPÓSITO: Utilidad de línea de comandos para registrar nuevos usuarios en Agendify.
#
# Uso:
#   venv\Scripts\python crear_usuario.py
# ============================================================================

from models.usuario import Usuario
import sys

def main():
    print("=============================================")
    print("   AGENDIFY - REGISTRO DE NUEVO USUARIO      ")
    print("=============================================\n")
    
    try:
        nombre = input("Ingrese el Nombre Completo: ").strip()
        email = input("Ingrese el Correo Electrónico: ").strip().lower()
        password = input("Ingrese la Contraseña (mínimo 6 caracteres): ").strip()
        
        # Validar entrada
        if not nombre or not email or not password:
            print("\n❌ Error: Todos los campos son obligatorios.")
            return

        # Verificar si el correo ya existe
        usuario_existente = Usuario.obtener_por_email(email)
        if usuario_existente:
            print(f"\n❌ Error: El correo '{email}' ya se encuentra registrado.")
            return

        # Instanciar y guardar modelo
        nuevo_usuario = Usuario(nombre=nombre, email=email, password=password)
        errores = nuevo_usuario.validar()
        
        if errores:
            print("\n❌ Errores de validación detectados:")
            for err in errores:
                print(f"  - {err}")
            return
            
        nuevo_usuario.guardar()
        print(f"\n✅ ¡Éxito! El usuario '{nombre}' ({email}) fue creado exitosamente y ya puede iniciar sesión.")
        
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    main()
