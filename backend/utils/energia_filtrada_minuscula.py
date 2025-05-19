#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

# Hardcodea aquí el input/output
INPUT_CSV  = 'backend/datos/energia_filtrada_con_totales.csv'
OUTPUT_CSV = 'backend/datos/energia_filtrada_con_totales.csv'

PAIS_MAP = {
    'France': 'francia',
    'Spain':  'espana',
    'Italy':  'italia',
}

def convertir_paises_pandas(in_path, out_path):
    # utf-8-sig descarta BOM si existiera
    df = pd.read_csv(in_path, encoding='utf-8-sig')  
    df['Pais'] = df['Pais'].map(PAIS_MAP).fillna(df['Pais']).str.lower()
    df.to_csv(out_path, index=False, encoding='utf-8')
    print(f"¡Listo! Generado: '{out_path}'")

if __name__ == "__main__":
    convertir_paises_pandas(INPUT_CSV, OUTPUT_CSV)
