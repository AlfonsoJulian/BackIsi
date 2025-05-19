import pandas as pd
import os

# 1. Definimos las categorías compatibles
COMPATIBLE = [
    "Coal, peat and oil shale",
    "Oil products",
    "Natural gas",
    "Nuclear",
    "Renewables and waste"
]

# 2. Ruta al CSV original (raw string para evitar errores con backslashes)
csv_path = r"backend\datos\fr,sp,it_filtrado.csv"

# 3. Leemos el CSV, forzando a NaN los valores “c”, “C” o vacíos
df = pd.read_csv(csv_path, na_values=["c", "C", ""])

# 4. (Opcional) Eliminamos cualquier columna 'Unnamed'
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

# 5. Detectamos las columnas de años (2008–2022)
year_cols = [col for col in df.columns if col.isdigit()]

# 6. Filtramos solo las filas con TipoEnergia compatible
df_filtered = df[df["TipoEnergia"].isin(COMPATIBLE)].copy()

# 7. Construimos una lista de diccionarios con las filas filtradas
filas = [row.to_dict() for _, row in df_filtered.iterrows()]

# 8. Para cada país e indicador, calculamos la fila "Total" sumando año a año
for pais in df_filtered["Pais"].unique():
    for indicador in df_filtered.loc[df_filtered["Pais"] == pais, "Indicador"].unique():
        sub = df_filtered[
            (df_filtered["Pais"] == pais) &
            (df_filtered["Indicador"] == indicador)
        ]
        suma = sub[year_cols].sum()
        total_row = {
            "Pais": pais,
            "TipoEnergia": "Total",
            "Indicador": indicador,
            **suma.to_dict()
        }
        filas.append(total_row)

# 9. Creamos el DataFrame resultado y lo guardamos a CSV
df_result = pd.DataFrame(filas)
output_path = "energia_filtrada_con_totales.csv"
df_result.to_csv(output_path, index=False)

print(f"Generado '{output_path}' con solo las categorías compatibles y sus totales.")
