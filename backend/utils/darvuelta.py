import pandas as pd

# 1. Leemos el CSV original
df = pd.read_csv("backend\datos\energia_filtrada_con_totales.csv")

# 2. Melt: convertimos las columnas de años en filas
df_melt = df.melt(
    id_vars=['pais', 'tipoenergia', 'indicador'],
    var_name='año',
    value_name='valor'
)

# 3. Pivot: llevamos tipoenergia a columnas
df_tidy = df_melt.pivot_table(
    index=['pais', 'indicador', 'año'],
    columns='tipoenergia',
    values='valor'
).reset_index()

# 4. Quitamos el nombre del índice de columnas
df_tidy.columns.name = None

# 5. Guardamos el resultado en un nuevo CSV
df_tidy.to_csv("backend\datos\energia_filtrada_con_totales_vuelta.csv", index=False)

print("no problema amigo")
