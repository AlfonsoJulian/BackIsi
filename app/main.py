from flask import Flask
from app.routes import routes  # Importamos el Blueprint

app = Flask(__name__)

# Registrar el Blueprint
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)
