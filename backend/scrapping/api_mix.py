import requests
import pandas as pd

def get_energy_mix(zone="IT"):
    # URL de la API y cabecera de autenticación
    url = f"https://api.electricitymap.org/v3/power-breakdown/latest?zone={zone}"
    headers = {"auth-token": "UaBrRwos3WkWtvqIN19d"}

    # Realiza la solicitud GET
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return None  # Devuelve None si la solicitud falla

    data = response.json()

    # Extrae la información relevante
    zone = data.get("zone")
    datetime_value = data.get("datetime")

    # Mezcla energética de consumo y producción
    consumption = data.get("powerConsumptionBreakdown", {})
    production = data.get("powerProductionBreakdown", {})

    #Preparamos los datos
    consumption_data = {
        "zone": zone,
        "datetime": datetime_value,
        "nuclear": consumption.get("nuclear", 0),
        "geothermal": consumption.get("geothermal", 0),
        "biomass": consumption.get("biomass", 0),
        "coal": consumption.get("coal", 0),
        "wind": consumption.get("wind", 0),
        "solar": consumption.get("solar", 0),
        "hydro": consumption.get("hydro", 0),
        "gas": consumption.get("gas", 0),
        "oil": consumption.get("oil", 0),
        "unknown": consumption.get("unknown", 0),
        "hydro discharge": consumption.get("hydro discharge", 0),
        "battery discharge": consumption.get("battery discharge", 0),
    }

    production_data = {
        "zone": zone,
        "datetime": datetime_value,
        "nuclear": production.get("nuclear", 0),
        "geothermal": production.get("geothermal", 0),
        "biomass": production.get("biomass", 0),
        "coal": production.get("coal", 0),
        "wind": production.get("wind", 0),
        "solar": production.get("solar", 0),
        "hydro": production.get("hydro", 0),
        "gas": production.get("gas", 0),
        "oil": production.get("oil", 0),
        "unknown": production.get("unknown", 0),
        "hydro discharge": production.get("hydro discharge", 0),
        "battery discharge": production.get("battery discharge", 0),
    }

    return consumption_data, production_data

# Llamada de demostración
if __name__ == "__main__":
    consumption_data, production_data = get_energy_mix()

    if consumption_data is None or production_data is None:
        print("Error al obtener datos de la API.")
        exit()

    print("\nEnergy Mix Consumption:\n", pd.DataFrame([consumption_data]).to_string(index=False), "\n")
    print("\nEnergy Mix Production:", pd.DataFrame([production_data]).to_string(index=False), "\n")
