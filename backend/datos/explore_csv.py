import pandas as pd

# Ruta al archivo CSV
# csv_path = "backend/datos/fr,sp,it_filtrado.csv"
csv_path = "backend/datos/electricity_prices.csv"

# Detectar separador automáticamente si fuera necesario
try:
    df = pd.read_csv(csv_path)
except Exception as e:
    print(f"❌ Error leyendo el CSV por defecto: {e}")
    print("🔎 Intentando con separador ';' y codificación 'latin1'...")
    df = pd.read_csv(csv_path, sep=';', encoding='latin1')

# Mostrar primeras filas
print("🔍 Primeras filas del CSV:\n")
print(df.head())

# Mostrar información básica
print("\n🧱 Información de columnas:")
print(df.dtypes)

print("\n🧼 Valores nulos por columna:")
print(df.isna().sum())

print("\n📊 Estadísticas descriptivas:")
print(df.describe(include='all', datetime_is_numeric=True))

# Limpiar nombres de columnas
df.columns = df.columns.str.strip()
cols = df.columns.tolist()

print(f"\n📄 Columnas en {csv_path}:")
for i, col in enumerate(cols):
    print(f"{i+1:>2}. {col}")

# Duplicados
print(f"\n🔁 Filas duplicadas: {df.duplicated().sum()}")

# Valores únicos en columnas pequeñas
print("\n🧩 Valores únicos por columna (si hay menos de 30):")
for col in cols:
    unique_vals = df[col].dropna().unique()
    if len(unique_vals) <= 30:
        print(f"- {col} ({len(unique_vals)}): {unique_vals}")

# Intento de detección automática de claves útiles
for key in ['country', 'date', 'region', 'iso', 'location', 'area']:
    if key in df.columns:
        print(f"\n🗝️ Columna clave detectada: '{key}' — {df[key].unique()[:10]}")
