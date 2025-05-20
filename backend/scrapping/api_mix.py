#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Obtiene mix de consumo y producción para FR, ES e IT y convierte
las categorías de energía a minúscula y camelCase,
mostrando los nombres completos de los países.
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
        result = {
            # aquí sustituimos la sigla por el nombre completo
            "zona": ZONE_NAMES.get(zone, zone),
            "datetime": ts
        }
        renew_sum = sum(safe(d, k) for k in mapping["renewables"])
        for key in ["coal", "oil", "gas", "nuclear"]:
            cat = mapping[key]
            label = to_camel_case(cat)
            result[label] = safe(d, key)
        label_ren = to_camel_case("Renewables and waste")
        result[label_ren] = renew_sum
        total = sum(result[to_camel_case(mapping[k])] for k in ["coal", "oil", "gas", "nuclear"]) + renew_sum
        result[to_camel_case("Total")] = total
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

    pd.set_option("display.width", 120)
    print("\n**Consumo** (MW):")
    print(df_cons.to_string(index=False))

    print("\n**Producción** (MW):")
    print(df_prod.to_string(index=False))
