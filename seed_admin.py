from models.usuario import Usuario
import sys

def create_admin():
    email = "admin@agendify.com"
    password = "admin123"
    nombre = "Administrador"

    usuario = Usuario.obtener_por_email(email)
    if usuario:
        print("El usuario admin ya existe.")
    else:
        nuevo_usuario = Usuario(nombre=nombre, email=email, password=password)
        errores = nuevo_usuario.validar()
        if errores:
            print(f"Errores al crear admin: {errores}")
        else:
            nuevo_usuario.guardar()
            print("Usuario admin creado exitosamente.")

if __name__ == "__main__":
    create_admin()
