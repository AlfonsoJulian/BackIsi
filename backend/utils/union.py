#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

# 1) Leer el CSV de entrada (cámbialo si tu fichero se llama distinto)
df = pd.read_csv('backend/datos/precios_electricidad_lower.csv', encoding='utf-8')

# 2) Extraer el año de la columna 'Fecha'
df['Año'] = df['Fecha'].str.extract(r'(\d{4})').astype(int)

# 3) Filtrar años entre 2008 y 2022
df = df[df['Año'].between(2008, 2022)]

# 4) Agrupar por País y Año y calcular la media
cols_precio = ['Precio elec. sin imp. €/kWh', 'Precio elec. €/kWh']
media = (
    df
    .groupby(['País', 'Año'], as_index=False)[cols_precio]
    .mean()
    .round(1)  # opcional: redondear a 1 decimal
)

# 5) Guardar y mostrar
media.to_csv('backend/datos/precios_electricidad_lower.csv', index=False, encoding='utf-8')
print(media)
