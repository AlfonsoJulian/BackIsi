import pandas as pd
import sqlite3
import unicodedata
import os

# Ruta al CSV original
csv_path = "fr,sp,it_filtrado.csv"

# Ruta a la base de datos
db_path = "bd_energy.db"

# === 1. Cargar el CSV ===
df = pd.read_csv(csv_path)

# === 2. Eliminar columna sobrante ===
if 'Unnamed: 18' in df.columns:
    df = df.drop(columns=['Unnamed: 18'])

# === 3. Reemplazar valores no numéricos por NaN ===
df.replace(to_replace=['c', 'C', '', ' '], value=pd.NA, inplace=True)

# === 4. Convertir columnas de años a valores numéricos ===
year_cols = [col for col in df.columns if col.isdigit()]
df[year_cols] = df[year_cols].apply(pd.to_numeric, errors='coerce')

# === 5. Renombrar columnas a snake_case ===
df = df.rename(columns={
    'Pais': 'pais',
    'TipoEnergia': 'tipo_energia',
    'Indicador': 'indicador'
})

# === 6. Convertir tabla a formato largo ===
df_long = df.melt(
    id_vars=['pais', 'tipo_energia', 'indicador'],
    value_vars=year_cols,
    var_name='anio',
    value_name='valor'
)

# === 7. Convertir columna 'anio' a int ===
df_long['anio'] = df_long['anio'].astype(int)

# === 8. Normalizar nombres de país (tildes, minúsculas, traducción) ===
def normalizar_pais(pais):
    pais = str(pais)
    # Eliminar tildes y espacios
    pais = unicodedata.normalize('NFKD', pais).encode('ASCII', 'ignore').decode('utf-8').lower().strip()
    # Traducción a inglés normalizado
    traducciones = {
        'espana': 'spain',
        'españa': 'spain',
        'francia': 'france',
        'italia': 'italy'
    }
    return traducciones.get(pais, pais)

df_long['pais'] = df_long['pais'].apply(normalizar_pais)

# === 9. Eliminar duplicados si existen ===
df_long = df_long.drop_duplicates()

# === 10. Guardar en SQLite ===
conn = sqlite3.connect(db_path)

df_long.to_sql('energia', conn, if_exists='replace', index=False)

conn.close()

print(f"✅ Datos insertados correctamente en la tabla 'energia' de '{os.path.abspath(db_path)}'")
