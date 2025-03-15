from backend.models import EnergyMix
import requests

class EnergyAPIClient:
    BASE_URL = "https://api.electricitymap.org/v3/power-breakdown/latest"

    def __init__(self, auth_token):
        self.auth_token = auth_token

    def get_energy_mix(self, zone="IT"):
        """Obtiene la mezcla energética de una zona específica usando la API."""
        url = f"{self.BASE_URL}?zone={zone}"
        headers = {"auth-token": self.auth_token}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error en la API: {response.status_code}")
            return None, None

        data = response.json()

        # Convertir datos en objetos EnergyMix
        consumption = EnergyMix(zone=zone, datetime=data.get("datetime"), **data["powerConsumptionBreakdown"])
        production = EnergyMix(zone=zone, datetime=data.get("datetime"), **data["powerProductionBreakdown"])

        return consumption, production
