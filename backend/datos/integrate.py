import pandas as pd

# === LEER Y LIMPIAR DATASET IEA ===
df_iea = pd.read_csv("backend/datos/fr,sp,it_filtrado.csv")  # Este es el IEA real

# Mostrar columnas para verificación
print("Columnas en df_iea:", df_iea.columns.tolist())

# Validar columnas necesarias
if not {"Pais", "TipoEnergia", "Indicador"}.issubset(df_iea.columns):
    raise ValueError("⚠ El archivo fr,sp,it_filtrado.csv no es el esperado.")

# Eliminar columnas no deseadas
df_iea = df_iea.loc[:, ~df_iea.columns.str.startswith("Unnamed:")]

# Reemplazar 'c' por NaN
df_iea.replace("c", pd.NA, inplace=True)

# Convertir años a float
for year in range(2008, 2023):
    col = str(year)
    if col in df_iea.columns:
        df_iea[col] = pd.to_numeric(df_iea[col], errors='coerce')

# Formato largo: una fila por (País, Tipo, Indicador, Año)
df_iea_long = df_iea.melt(id_vars=["Pais", "TipoEnergia", "Indicador"],
                          var_name="Anio",
                          value_name="Valor_PJ")

# Filtrar solo el consumo final
df_iea_consumo = df_iea_long[df_iea_long["Indicador"] == "Total final consumption (PJ)"]

# === LEER Y PROCESAR DATASET DE PRECIOS ===
df_price = pd.read_csv("backend/datos/electricity_prices.csv")  # Este es el scraping

# Extraer año de la columna 'Fecha'
df_price["Anio"] = df_price["Fecha"].str.extract(r"(\d{4})")

# Vista previa
print("\n🧪 Vista previa de años extraídos:")
print(df_price[["Fecha", "Anio"]].head(10))

# Eliminar filas sin año
df_price = df_price.dropna(subset=["Anio"])

# Convertir a entero
df_price["Anio"] = df_price["Anio"].astype(int)

# Agrupar por país y año
df_price_yearly = df_price.groupby(["País", "Anio"], as_index=False).agg({
    "Precio elec. €/kWh": "mean"
})

# Normalizar nombres de países
df_price_yearly["País"] = df_price_yearly["País"].replace({
    "Italia": "Italy",
    "Francia": "France",
    "España": "Spain"
})

# Convertir Anio a int para poder hacer merge
df_iea_consumo["Anio"] = df_iea_consumo["Anio"].astype(int)

# Mostrar resumen de claves para el merge
print("\n🔍 Países únicos en IEA:")
print(sorted(df_iea_consumo["Pais"].unique()))
print("\n🔍 Países únicos en precios:")
print(sorted(df_price_yearly["País"].unique()))
print("\n📆 Años únicos en IEA:")
print(sorted(df_iea_consumo["Anio"].unique()))
print("\n📆 Años únicos en precios:")
print(sorted(df_price_yearly["Anio"].unique()))

# === UNIÓN DE AMBOS DATASETS ===
df_merged = pd.merge(df_iea_consumo, df_price_yearly,
                     left_on=["Pais", "Anio"],
                     right_on=["País", "Anio"],
                     how="inner")

# === CONVERSIÓN Y COSTE ESTIMADO ===
PJ_TO_KWH = 1e+15 / 3.6e+6  # ≈ 2.78e+8 kWh
df_merged["Consumo_kWh"] = df_merged["Valor_PJ"] * PJ_TO_KWH
df_merged["Coste_estimado_€"] = df_merged["Consumo_kWh"] * df_merged["Precio elec. €/kWh"]

# === GUARDAR RESULTADO FINAL ===
df_merged.to_csv("backend/datos/consumo_vs_precio_integrado.csv", index=False)
print("✅ Integración completada. Archivo guardado en 'backend/datos/consumo_vs_precio_integrado.csv'")
