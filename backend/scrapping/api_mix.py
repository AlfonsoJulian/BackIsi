#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sqlite3
import re

# — tokens de la API
TOKENS = {
    "FR": "rzkgb31u0rPxQo8Zg1Um",
    "ES": "cx1tJ4xxAOUOWcua0whK",
    "IT": "j0plnlEgjaTrNJGLXQOO",
}

# — nombres que van a la tabla pais (coinciden con lo que quieres)
ZONE_NAMES = {
    "FR": "francia",
    "ES": "espana",
    "IT": "italia",
}

# de MWh a PJ
MWH_TO_PJ      = 3.6e-6
# para llevar de valor horario a anual: 24 horas × 365 días
HOUR_TO_YEAR   = 24 * 365

DB_PATH = r'C:\Users\Usuario\Desktop\facultad\cuarto\2CUATRI\isi\practicas\BackIsi\backend\bd\energy.db'

def to_camel_case(s: str) -> str:
    parts = re.findall(r'[A-Za-z0-9]+', s)
    parts = [p.lower() for p in parts]
    return parts[0] + ''.join(p.title() for p in parts[1:]) if parts else ''

def get_comparable_mix(zone: str, token: str):
    url = f"https://api.electricitymap.org/v3/power-breakdown/latest?zone={zone}"
    resp = requests.get(url, headers={"auth-token": token})
    resp.raise_for_status()
    data = resp.json()
    ts   = data["datetime"]
    cons = data["powerConsumptionBreakdown"]
    prod = data["powerProductionBreakdown"]

    def safe(d, k):
        return float(d.get(k) or 0.0)

    def extract(d):
        mapping = {
            "coal":       "Coal, peat and oil shale",
            "oil":        "Oil products",
            "gas":        "Natural gas",
            "nuclear":    "Nuclear",
            "renewables": ["wind","solar","hydro","biomass","geothermal"]
        }

        out = {
            "pais":  ZONE_NAMES[zone],
            "fecha": ts
        }

        # sumatorio de renovables
        renew = sum(safe(d, k) for k in mapping["renewables"])

        # extraemos valores principales
        for key in ("coal","oil","gas","nuclear"):
            label = to_camel_case(mapping[key])
            out[label] = safe(d, key)

        out[to_camel_case("Renewables and waste")] = renew

        # total instantáneo
        total = sum(out[to_camel_case(mapping[k])] for k in ("coal","oil","gas","nuclear")) + renew
        out[to_camel_case("Total")] = total

        # —— Conversión de MWh a PJ
        for k in list(out):
            if k not in ("pais", "fecha"):
                out[k] *= MWH_TO_PJ

        # —— Conversión de valor horario a anual (×24h ×365d)
        for k in list(out):
            if k not in ("pais", "fecha"):
                out[k] *= HOUR_TO_YEAR

        return out

    return extract(cons), extract(prod)


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # 1) Aseguramos que existan los países en pais(pais)
    for name in ZONE_NAMES.values():
        cur.execute("INSERT OR IGNORE INTO pais(pais) VALUES(?)", (name,))

    # 2) Obtenemos y metemos registros
    for zone, token in TOKENS.items():
        cons, prod = get_comparable_mix(zone, token)
        for indicador, rec in [
            ("totalFinalConsumptionPj", cons),
            ("productionPj",            prod),
        ]:
            cur.execute("""
                INSERT OR REPLACE INTO actual_consumo_produccion
                  (pais, indicador, fecha,
                   coal_peat_oil_shale, natural_gas, nuclear,
                   oil_products, renewables_and_waste, total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rec["pais"],
                indicador,
                rec["fecha"],
                rec.get("coalPeatAndOilShale"),
                rec.get("naturalGas"),
                rec.get("nuclear"),
                rec.get("oilProducts"),
                rec.get("renewablesAndWaste"),
                rec.get("total"),
            ))

    conn.commit()
    conn.close()
    print("Datos actuales insertados en actual_consumo_produccion (PJ anuales).")
