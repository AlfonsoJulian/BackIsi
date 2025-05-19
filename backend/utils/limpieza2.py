import pandas as pd

# Lee tu CSV (ajusta 'archivo.csv' y el separador si es necesario)
df = pd.read_csv('backend/datos/fr,sp,it.csv')

# Filtra por los valores que te interesan en la columna de indicador
mask = df['Indicador'].isin(['Production (PJ)', 'Total final consumption (PJ)'])
df_filtrado = df[mask]

# Guarda o muestra el resultado
df_filtrado.to_csv('backend/datos/fr,sp,it_filtrado.csv', index=False)
print(df_filtrado)
