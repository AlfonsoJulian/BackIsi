from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests

app = Flask(__name__)

# Función para crear la base de datos y las tablas si no existen
def init_db():
    conn = sqlite3.connect('bd_energy.db')
    cursor = conn.cursor()
    # Tabla existente para proyectos de energía
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bd_energy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            country TEXT NOT NULL,
            price REAL NOT NULL,
            GWh REAL NOT NULL
        )
    """)
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
    conn = sqlite3.connect('bd_energy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bd_energy")
    bd_energy_projects = cursor.fetchall()
    conn.close()
    return render_template('index.html', bd_energy_projects=bd_energy_projects)

@app.route('/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        title = request.form['title']
        country = request.form['country']
        price = request.form['price']
        GWh = request.form['GWh']
        
        conn = sqlite3.connect('bd_energy.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bd_energy (title, country, price, GWh) VALUES (?, ?, ?, ?)",
                       (title, country, price, GWh))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_project.html')

@app.route('/delete/<int:project_id>', methods=['GET'])
def delete_project(project_id):
    conn = sqlite3.connect('bd_energy.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bd_energy WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/show_consumption')
def show_consumption():
    conn = sqlite3.connect('bd_energy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM energy_consumption")
    consumption_data = cursor.fetchall()
    conn.close()
    return render_template('show_consumption.html', consumption_data=consumption_data)

@app.route('/show_production')
def show_production():
    conn = sqlite3.connect('bd_energy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM energy_production")
    production_data = cursor.fetchall()
    conn.close()
    return render_template('show_production.html', production_data=production_data)

# Ruta para obtener datos de la API e insertarlos en las tablas de consumo y producción
@app.route('/update_data')
def update_data():
    url = "https://api.electricitymap.org/v3/power-breakdown/latest?zone=IT"
    headers = {"auth-token": "UaBrRwos3WkWtvqIN19d"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        zone = data.get("zone")
        datetime_val = data.get("datetime")
        consumption = data.get("powerConsumptionBreakdown", {})
        production = data.get("powerProductionBreakdown", {})
        
        conn = sqlite3.connect('bd_energy.db')
        cursor = conn.cursor()
        
        # Insertar datos en la tabla energy_consumption
        cursor.execute("""
            INSERT INTO energy_consumption 
            (zone, datetime, nuclear, geothermal, biomass, coal, wind, solar, hydro, gas, oil, unknown, "hydro discharge", "battery discharge")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            zone,
            datetime_val,
            consumption.get("nuclear"),
            consumption.get("geothermal"),
            consumption.get("biomass"),
            consumption.get("coal"),
            consumption.get("wind"),
            consumption.get("solar"),
            consumption.get("hydro"),
            consumption.get("gas"),
            consumption.get("oil"),
            consumption.get("unknown"),
            consumption.get("hydro discharge"),
            consumption.get("battery discharge")
        ))
        
        # Insertar datos en la tabla energy_production
        cursor.execute("""
            INSERT INTO energy_production 
            (zone, datetime, nuclear, geothermal, biomass, coal, wind, solar, hydro, gas, oil, unknown, "hydro discharge", "battery discharge")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            zone,
            datetime_val,
            production.get("nuclear"),
            production.get("geothermal"),
            production.get("biomass"),
            production.get("coal"),
            production.get("wind"),
            production.get("solar"),
            production.get("hydro"),
            production.get("gas"),
            production.get("oil"),
            production.get("unknown"),
            production.get("hydro discharge"),
            production.get("battery discharge")
        ))
        conn.commit()
        conn.close()
        return "Datos de consumo y producción actualizados en la base de datos."
    else:
        return "Error al obtener datos de la API."

# Inicializar la base de datos al arrancar la aplicación
init_db()

if __name__ == "__main__":
    app.run(debug=True)
