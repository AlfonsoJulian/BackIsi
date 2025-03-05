
import sqlite3

# Conectar a la base de datos SQLite
conn = sqlite3.connect('../energy.db')

# Crear un cursor para ejecutar comandos SQL
cursor = conn.cursor()

# Insertar algunos datos de ejemplo
cursor.execute("""
    INSERT INTO energy (titulo, pais, precio, GWh) VALUES
    ('Solar Spain', 'Spain', 5, 200.0),
    ('Solar Mexico', 'Mexico', 2, 20.0)
""")

# Confirmar la inserción
conn.commit()

print("Datos insertados correctamente.")

# Cerrar la conexión
conn.close()



