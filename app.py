from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import backend.scrapping.api_mix as api_mix  # OJO: importamos como api_mix

app = Flask(__name__)
db_name = "bd_energy.db"

# Función para crear la base de datos y las tablas si no existen
def init_db():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Nueva tabla para la mezcla energética de consumo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS energy_consumption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone TEXT,
            datetime TEXT,
            nuclear INTEGER,
            geothermal INTEGER,
            biomass INTEGER,
            coal INTEGER,
            wind INTEGER,
            solar INTEGER,
            hydro INTEGER,
            gas INTEGER,
            oil INTEGER,
            unknown INTEGER,
            "hydro discharge" INTEGER,
            "battery discharge" INTEGER
        )
    """)

    # Nueva tabla para la mezcla energética de producción
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS energy_production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone TEXT,
            datetime TEXT,
            nuclear INTEGER,
            geothermal INTEGER,
            biomass INTEGER,
            coal INTEGER,
            wind INTEGER,
            solar INTEGER,
            hydro INTEGER,
            gas INTEGER,
            oil INTEGER,
            unknown INTEGER,
            "hydro discharge" INTEGER,
            "battery discharge" INTEGER
        )
    """)

    conn.commit()
    conn.close()

@app.route('/')
def index():
    # Simplemente renderizamos la plantilla 'index.html'
    return render_template('index.html')

@app.route('/show_consumption')
def show_consumption():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Obtenemos todos los registros de la tabla 'energy_consumption'
    cursor.execute("SELECT * FROM energy_consumption")
    consumption_data = cursor.fetchall()

    conn.close()
    # Pasamos los datos a la plantilla 'show_consumption.html'
    return render_template('show_consumption.html', consumption_data=consumption_data)

@app.route('/show_production')
def show_production():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Obtenemos todos los registros de la tabla 'energy_production'
    cursor.execute("SELECT * FROM energy_production")
    production_data = cursor.fetchall()

    conn.close()
    # Pasamos los datos a la plantilla 'show_production.html'
    return render_template('show_production.html', production_data=production_data)

# Ruta para obtener datos de la API e insertarlos en las tablas de consumo y producción
@app.route('/update_data', methods = ['POST'])
def update_data():
    # Obtener los datos de consumo y producción desde api_mix
    consumption_data, production_data = api_mix.get_energy_mix()

    if consumption_data is None or production_data is None:
        return "Error al obtener datos de la API."

    # Conectar a la base de datos
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Insertar datos en la tabla energy_consumption
    cursor.execute("""
        INSERT INTO energy_consumption 
        (zone, datetime, nuclear, geothermal, biomass, coal, wind, solar, hydro, gas, oil, unknown, "hydro discharge", "battery discharge")
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        consumption_data["zone"],
        consumption_data["datetime"],
        consumption_data["nuclear"],
        consumption_data["geothermal"],
        consumption_data["biomass"],
        consumption_data["coal"],
        consumption_data["wind"],
        consumption_data["solar"],
        consumption_data["hydro"],
        consumption_data["gas"],
        consumption_data["oil"],
        consumption_data["unknown"],
        consumption_data["hydro discharge"],
        consumption_data["battery discharge"]
    ))

    # Insertar datos en la tabla energy_production
    cursor.execute("""
        INSERT INTO energy_production 
        (zone, datetime, nuclear, geothermal, biomass, coal, wind, solar, hydro, gas, oil, unknown, "hydro discharge", "battery discharge")
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        production_data["zone"],
        production_data["datetime"],
        production_data["nuclear"],
        production_data["geothermal"],
        production_data["biomass"],
        production_data["coal"],
        production_data["wind"],
        production_data["solar"],
        production_data["hydro"],
        production_data["gas"],
        production_data["oil"],
        production_data["unknown"],
        production_data["hydro discharge"],
        production_data["battery discharge"]
    ))

    # Confirmar los cambios y cerrar la conexión
    conn.commit()
    conn.close()

    return "Datos de consumo y producción actualizados en la base de datos."

# Inicializar la base de datos al arrancar la aplicación
init_db()

if __name__ == "__main__":
    # Iniciar la aplicación Flask en modo debug
    app.run(debug=True)
