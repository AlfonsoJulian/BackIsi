import requests
import pandas as pd

# URL de la API y cabecera de autenticación
url = "https://api.electricitymap.org/v3/power-breakdown/latest?zone=IT"
headers = {"auth-token": "UaBrRwos3WkWtvqIN19d"}

# Realiza la solicitud GET
response = requests.get(url, headers=headers)
data = response.json()

# Extrae la información relevante
zone = data.get("zone")               # País (o zona)
datetime_value = data.get("datetime") # Fecha y hora de la información

# Mezcla energética de consumo y producción
consumption = data.get("powerConsumptionBreakdown", {})
production = data.get("powerProductionBreakdown", {})

# Crea una tabla (DataFrame) para el consumo
consumption_data = {"zone": zone, "datetime": datetime_value}
consumption_data.update(consumption)  # Agrega las claves de consumo
df_consumption = pd.DataFrame([consumption_data])

# Crea una tabla (DataFrame) para la producción
production_data = {"zone": zone, "datetime": datetime_value}
production_data.update(production)    # Agrega las claves de producción
df_production = pd.DataFrame([production_data])

# Muestra las tablas
print("Energy Mix Consumption:")
print(df_consumption)
print("\nEnergy Mix Production:")
print(df_production)
