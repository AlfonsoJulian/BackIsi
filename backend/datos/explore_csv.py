import pandas as pd

# csv_path = "backend/datos/fr,sp,it_filtrado.csv"
# csv_path = "backend/datos/electricity_prices.csv"
csv_path = "backend/datos/consumo_vs_precio_integrado.csv"


df = pd.read_csv(csv_path)

print(df.head())           # Primeras filas
print(df.columns)          # Nombres de columnas
print(df.dtypes)           # Tipos de datos
print(df.isna().sum())     # Valores nulos


cols = df.columns.str.strip().tolist()

print(f"\n📄 Columnas en {csv_path}:")
for i, col in enumerate(cols):
    print(f"{i+1:>2}. {col}")

