from BBDD import createBBDD, modifyBBDD, readBBDD

from flask import Flask

# Crear una instancia de la clase Flask
app = Flask(__name__)

# Definir una ruta básica
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Ejecutar el servidor en localhost
if __name__ == "__main__":
    app.run(debug=True)
