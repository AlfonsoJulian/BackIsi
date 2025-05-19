import requests
import pandas as pd

def get_comparable_mix(zone="IT"):
    url = f"https://api.electricitymap.org/v3/power-breakdown/latest?zone={zone}"
    headers = {"auth-token": "rzkgb31u0rPxQo8Zg1Um"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return None, None

    data = resp.json()
    ts = data["datetime"]
    cons = data.get("powerConsumptionBreakdown", {})
    prod = data.get("powerProductionBreakdown", {})

    # helper: si v es None devuelve 0.0
    def safe(d, key):
        v = d.get(key)
        return 0.0 if v is None else v

    def extract(d):
        coal       = safe(d, "coal")
        oil        = safe(d, "oil")
        gas        = safe(d, "gas")
        nuclear    = safe(d, "nuclear")
        renewables = sum(safe(d, k) for k in ["wind","solar","hydro","biomass","geothermal"])
        total      = coal + oil + gas + nuclear + renewables

        return {
            "zone": zone,
            "datetime": ts,
            "Coal, peat and oil shale": coal,
            "Oil products": oil,
            "Natural gas": gas,
            "Nuclear": nuclear,
            "Renewables and waste": renewables,
            "Total": total
        }

    return extract(cons), extract(prod)


if __name__ == "__main__":
    cons, prod = get_comparable_mix("FR")  # p. ej. Francia

    if cons is None:
        print("Error al obtener datos de la API")
        exit(1)

    df_cons = pd.DataFrame([cons])
    df_prod = pd.DataFrame([prod])

    print("\n**Consumo** (MW):")
    print(df_cons.to_string(index=False))

    print("\n**Producción** (MW):")
    print(df_prod.to_string(index=False))
