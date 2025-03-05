import sqlite3

# Conectar a la base de datos SQLite (se crea automáticamente si no existe)
conn = sqlite3.connect('energy.db')

# Crear un cursor para ejecutar comandos SQL
cursor = conn.cursor()

# Crear una tabla llamada 'energy'
cursor.execute("""
    CREATE TABLE IF NOT EXISTS energy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        pais TEXT,
        precio REAL,
        GWh REAL
    )
""")

# Confirmar que la tabla se creó correctamente
print("Tabla 'energy' creada o ya existe.")