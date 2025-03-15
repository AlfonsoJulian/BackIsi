from backend.models import EnergyMix, Country
from backend.database import DatabaseManager
from scrapping.api_client import EnergyAPIClient

class EnergyService:
    """Servicio que obtiene datos y los almacena en la BD."""
    def __init__(self):
        self.db = DatabaseManager()
        self.api_client = EnergyAPIClient(auth_token="UaBrRwos3WkWtvqIN19d")

    def update_country_energy_data(self, country_name="IT"):
        """Obtiene datos desde la API y los almacena en la BD como objetos."""
        consumption, production = self.api_client.get_energy_mix(country_name)

        if not consumption or not production:
            return "Error: No se pudieron obtener datos de la API."

        country = Country(country_name)
        country.set_energy_data(consumption, production)

        # Insertar los datos en la BD
        self.db.execute_query("""
            INSERT INTO energy_consumption 
            (zone, datetime, nuclear, geothermal, biomass, coal, wind, solar, hydro, gas, oil, unknown, hydro_discharge, battery_discharge)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, country.consumption.to_tuple())

        self.db.execute_query("""
            INSERT INTO energy_production 
            (zone, datetime, nuclear, geothermal, biomass, coal, wind, solar, hydro, gas, oil, unknown, hydro_discharge, battery_discharge)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, country.production.to_tuple())

        return f"Datos de {country_name} actualizados en la base de datos."
