import pandas as pd
import sqlite3
import unicodedata
import os

# Ruta al CSV original
csv_path = "electricity_prices.csv"

# Ruta a la base de datos
db_path = "bd_energy.db"

# === 1. Leer CSV ===
df = pd.read_csv(csv_path)

# === 2. Renombrar columnas a snake_case ===
df = df.rename(columns={
    'Fecha': 'fecha',
    'Precio elec. sin imp. €/kWh': 'precio_sin_impuestos',
    'Precio elec. €/kWh': 'precio_con_impuestos',
    'País': 'pais'
})

# === 3. Normalizar nombres de país ===
def normalizar_pais(pais):
    pais = str(pais)
    pais = unicodedata.normalize('NFKD', pais).encode('ASCII', 'ignore').decode('utf-8').lower().strip()
    traducciones = {
        'espana': 'spain',
        'españa': 'spain',
        'francia': 'france',
        'italia': 'italy'
    }
    return traducciones.get(pais, pais)

df['pais'] = df['pais'].apply(normalizar_pais)

# === 4. Limpiar y convertir columna fecha ===
meses_es = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
}

def limpiar_texto(texto):
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto

def convertir_fecha(fecha_str):
    fecha_str = limpiar_texto(fecha_str)
    partes = fecha_str.split()
    if len(partes) == 2:
        mes = meses_es.get(partes[0], None)
        anio = partes[1]
        if mes and anio.isdigit():
            return f"{anio}-{mes}-01"
    return pd.NaT

df['fecha'] = df['fecha'].apply(convertir_fecha)
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

# === 5. Convertir precios de milésimas a €/kWh ===
df['precio_sin_impuestos'] = df['precio_sin_impuestos'] / 10000
df['precio_con_impuestos'] = df['precio_con_impuestos'] / 10000

# === 6. Eliminar filas con NaN en columnas clave ===
df = df.dropna(subset=['fecha', 'precio_sin_impuestos', 'precio_con_impuestos', 'pais'])

# === 7. Eliminar filas de Francia ===
df = df[df['pais'] != 'france']

# === 8. Eliminar duplicados ===
df = df.drop_duplicates()

# === 9. Guardar en SQLite ===
conn = sqlite3.connect(db_path)
df.to_sql('precios', conn, if_exists='replace', index=False)
conn.close()

print(f"✅ Datos insertados correctamente (sin Francia) en la tabla 'precios' de '{os.path.abspath(db_path)}'")
