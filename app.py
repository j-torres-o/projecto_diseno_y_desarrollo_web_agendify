# Importamos la clase Flask y la función render_template del módulo flask
# Flask: Es la herramienta principal para crear nuestra aplicación web.
# render_template: Nos permite mostrar archivos HTML que están en la carpeta 'templates'.
from flask import Flask, render_template

# Creamos una instancia de la aplicación Flask.
# El argumento __name__ le dice a Flask dónde buscar archivos como plantillas y estáticos.
app = Flask(__name__)

# Definimos la ruta principal ('/') de nuestra aplicación.
# Un decorador (@app.route) asocia una dirección URL con una función de Python.
@app.route('/')
def index():
    # Esta función se ejecuta cuando alguien entra a la página de inicio.
    # Devuelve el contenido del archivo 'index.html'.
    return render_template('index.html')

# Punto de entrada de la aplicación.
# El bloque 'if __name__ == "__main__":' asegura que el servidor solo se inicie
# si ejecutamos este archivo directamente (no si lo importamos en otro lado).
if __name__ == '__main__':
    # Iniciamos el servidor en modo depuración (debug=True) para ver errores detallados.
    # El puerto por defecto es el 5000.
    app.run(debug=True, port=5000)
