from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Crear la base de datos y la tabla si no existe
def init_db():
    conn = sqlite3.connect('bd_energy.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bd_energy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            country TEXT NOT NULL,
            price REAL NOT NULL,
            GWh REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Ruta principal para ver los proyectos de energía
@app.route('/')
def index():
    conn = sqlite3.connect('bd_energy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bd_energy")
    bd_energy_projects = cursor.fetchall()
    conn.close()
    return render_template('index.html', bd_energy_projects=bd_energy_projects)

# Ruta para agregar un proyecto de energía
@app.route('/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        title = request.form['title']
        country = request.form['country']
        price = request.form['price']
        GWh = request.form['GWh']
        
        conn = sqlite3.connect('bd_energy.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bd_energy (title, country, price, GWh) VALUES (?, ?, ?, ?)", (title, country, price, GWh))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_project.html')

# Ruta para eliminar un proyecto de energía
@app.route('/delete/<int:project_id>', methods=['GET'])
def delete_project(project_id):
    conn = sqlite3.connect('bd_energy.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bd_energy WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Iniciar la base de datos al arrancar la aplicación
init_db()

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)
