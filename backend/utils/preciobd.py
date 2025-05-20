import os
import sqlite3
import csv

# 1) Ruta absoluta a la BD, con raw string para que no haga escapes
DB_PATH = r'C:\Users\Usuario\Desktop\facultad\cuarto\2CUATRI\isi\practicas\BackIsi\backend\bd\energy.db'
CSV_PATH = r'C:\Users\Usuario\Desktop\facultad\cuarto\2CUATRI\isi\practicas\BackIsi\backend\datos\precios_electricidad_lower.csv'

print("Conectando a:", DB_PATH)
# Asegura que exista la carpeta
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 2) Conexión
conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()
cur.execute('PRAGMA foreign_keys = ON;')

# 3) Insertamos CSV
with open(CSV_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        pais = row['pais']
        anio = int(row['anio'])
        impuesto = float(row['precioKWImpuesto']) if row['precioKWImpuesto'] else None
        precio   = float(row['precioKW'])          if row['precioKW']          else None

        cur.execute('''
            INSERT OR REPLACE INTO historico_precio
              (pais, anio, precio_kw_impuesto, precio_kw)
            VALUES (?, ?, ?, ?)
        ''', (pais, anio, impuesto, precio))

conn.commit()
conn.close()
print("¡Datos cargados correctamente!")

