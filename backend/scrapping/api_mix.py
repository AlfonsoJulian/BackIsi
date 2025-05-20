#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Obtiene mix de consumo y producción para Francia, España e Italia,
convierte las categorías de energía a camelCase, muestra nombres completos
y transforma los valores de MW a PJ (por hora).
"""

import requests
import pandas as pd
import re

# Mapeo de zonas a sus tokens
TOKENS = {
    "FR": "rzkgb31u0rPxQo8Zg1Um",
    "ES": "cx1tJ4xxAOUOWcua0whK",
    "IT": "j0plnlEgjaTrNJGLXQOO",
}

# Mapeo de siglas a nombres completos
ZONE_NAMES = {
    "FR": "Francia",
    "ES": "España",
    "IT": "Italia",
}

# Factor de conversión: 1 MW sostenido 1h → 3.6 GJ = 3.6e-6 PJ
MWH_TO_PJ = 3.6e-6

def to_camel_case(s: str) -> str:
    parts = re.findall(r'[A-Za-z0-9]+', s)
    if not parts:
        return ''
    parts = [p.lower() for p in parts]
    return parts[0] + ''.join(p.title() for p in parts[1:])

def get_comparable_mix(zone: str, auth_token: str):
    url = f"https://api.electricitymap.org/v3/power-breakdown/latest?zone={zone}"
    headers = {"auth-token": auth_token}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error {resp.status_code} para zona {zone}")
        return None, None

    data = resp.json()
    ts = data.get("datetime")
    cons = data.get("powerConsumptionBreakdown", {})
    prod = data.get("powerProductionBreakdown", {})

    def safe(d, key):
        v = d.get(key)
        return 0.0 if v is None else v

    def extract(d):
        mapping = {
            "coal": "Coal, peat and oil shale",
            "oil": "Oil products",
            "gas": "Natural gas",
            "nuclear": "Nuclear",
            "renewables": ["wind", "solar", "hydro", "biomass", "geothermal"]
        }
        # zona y datetime sin convertir
        result = {
            "zona": ZONE_NAMES.get(zone, zone),
            "datetime": ts
        }
        # suma de renovables
        renew_sum = sum(safe(d, k) for k in mapping["renewables"])
        # categorías simples
        for key in ["coal", "oil", "gas", "nuclear"]:
            cat = mapping[key]
            label = to_camel_case(cat)
            result[label] = safe(d, key)
        # renovables
        label_ren = to_camel_case("Renewables and waste")
        result[label_ren] = renew_sum
        # total
        total = sum(result[to_camel_case(mapping[k])] for k in ["coal", "oil", "gas", "nuclear"]) + renew_sum
        result[to_camel_case("Total")] = total

        # CONVERTIR de MW a PJ (por hora)
        for k, v in result.items():
            if k not in ("zona", "datetime"):
                result[k] = v * MWH_TO_PJ

        return result

    return extract(cons), extract(prod)

if __name__ == "__main__":
    all_cons = []
    all_prod = []
    for zone, token in TOKENS.items():
        cons, prod = get_comparable_mix(zone, token)
        if cons and prod:
            all_cons.append(cons)
            all_prod.append(prod)

    df_cons = pd.DataFrame(all_cons)
    df_prod = pd.DataFrame(all_prod)

    # Mostrar en ancho amplio
    pd.set_option("display.width", 120)
    print("\n**Consumo** (PJ por hora):")
    print(df_cons.to_string(index=False))

    print("\n**Producción** (PJ por hora):")
    print(df_prod.to_string(index=False))
