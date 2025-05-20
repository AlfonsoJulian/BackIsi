import os
import sqlite3
import csv

# 1) Rutas a tu BD y a tu CSV
DB_PATH  = r'C:\Users\Usuario\Desktop\facultad\cuarto\2CUATRI\isi\practicas\BackIsi\backend\bd\energy.db'
CSV_PATH = r'C:\Users\Usuario\Desktop\facultad\cuarto\2CUATRI\isi\practicas\BackIsi\backend\datos\energia_filtrada_con_totales_vuelta.csv'

# 2) Asegura que la carpeta de la BD existe
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 3) Conecta a SQLite
print(f"Conectando a {DB_PATH!r} …")
conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()
cur.execute('PRAGMA foreign_keys = ON;')

# 4) Abre el CSV y recorre cada fila
with open(CSV_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        pais    = row['pais']
        indicador = row['indicador']
        anio    = int(row['anio'])
        # Para cada valor numérico: convierto a float o dejo None si está vacío
        cps     = float(row['coalPeatAndOilShale']) if row['coalPeatAndOilShale'] else None
        gas     = float(row['naturalGas'])           if row['naturalGas']           else None
        nuc     = float(row['nuclear'])              if row['nuclear']              else None
        oil     = float(row['oilProducts'])          if row['oilProducts']          else None
        ren     = float(row['renewablesAndWaste'])   if row['renewablesAndWaste']   else None
        tot     = float(row['total'])                if row['total']                else None

        # 5) Inserta o reemplaza en historico_consumo_produccion
        cur.execute('''
            INSERT OR REPLACE INTO historico_consumo_produccion
              (pais, indicador, anio,
               coal_peat_oil_shale, natural_gas, nuclear,
               oil_products, renewables_and_waste, total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pais, indicador, anio,
              cps, gas, nuc,
              oil, ren, tot)
        )

# 6) Confirma y cierra
conn.commit()
conn.close()
print("¡Datos de consumo/producción cargados en historico_consumo_produccion!") 
