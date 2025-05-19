#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usando pandas:
Convierte todas las cadenas de un CSV a camelCase.
Lectura de 'energia_por_pais_es_lower.csv' y salida en 'energia_por_pais_camel.csv'.
"""

import pandas as pd
import re

# Rutas hardcodeadas
INPUT_CSV  = 'backend/datos/energia_filtrada_con_totales.csv'
OUTPUT_CSV = 'backend/datos/energia_filtrada_con_totales.csv'

def to_camel_case(s: str) -> str:
    palabras = re.findall(r'[A-Za-z0-9]+', s)
    if not palabras:
        return ''
    palabras = [w.lower() for w in palabras]
    return palabras[0] + ''.join(w.title() for w in palabras[1:])

def convertir_pandas(in_path, out_path):
    df = pd.read_csv(in_path, encoding='utf-8')
    # CamelCase en columnas
    df.columns = [to_camel_case(c) for c in df.columns]
    # Para cada columna de tipo object, aplicamos camelCase a los valores que contengan letras
    for col in df.select_dtypes(include=['object']):
        df[col] = df[col].fillna('').apply(
            lambda x: to_camel_case(x) if re.search(r'[A-Za-z]', x) else x
        )
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"¡Listo! Generado: '{out_path}'")

if __name__ == "__main__":
    convertir_pandas(INPUT_CSV, OUTPUT_CSV)
