#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convierte los nombres de los países a minúsculas en un CSV con datos de precios de electricidad.
Archivos de entrada y salida definidos directamente en el código.
"""

import csv

# Rutas hardcodeadas
INPUT_CSV = 'backend\datos\electricity_prices.csv'
OUTPUT_CSV = 'precios_electricidad_lower.csv'

def convertir_con_csv(input_path, output_path):
    with open(input_path, newline='', encoding='utf-8') as fin, \
         open(output_path, 'w', newline='', encoding='utf-8') as fout:
        lector = csv.DictReader(fin)
        campos = lector.fieldnames
        escritor = csv.DictWriter(fout, fieldnames=campos)
        escritor.writeheader()

        for fila in lector:
            fila['País'] = fila['País'].lower()
            escritor.writerow(fila)

if __name__ == "__main__":
    convertir_con_csv(INPUT_CSV, OUTPUT_CSV)
    print(f"¡Listo! Archivo generado: '{OUTPUT_CSV}'")
