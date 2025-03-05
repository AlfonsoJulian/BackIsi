import sqlite3

# Conectar a la base de datos SQLite
conn = sqlite3.connect('energy.db')

# Crear un cursor para ejecutar comandos SQL
cursor = conn.cursor()

# Leer los datos insertados
cursor.execute("SELECT * FROM energy")
resultados = cursor.fetchall()

# Mostrar los resultados
for fila in resultados:
    print(f"id: {fila[0]}, titulo: {fila[1]}, pais: {fila[2]}, precio: ${fila[3]}, GWh: {fila[4]}")

# Cerrar la conexión
conn.close()
