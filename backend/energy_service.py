from backend.database import DatabaseManager
from backend.models import EnergyMix, Country
from scrapping.api_client import EnergyAPIClient
from scrapping.scraping_prices import EnergyPriceScraper

class EnergyService:
    def __init__(self):
        self.db = DatabaseManager()
        self.api_client = EnergyAPIClient(auth_token="UaBrRwos3WkWtvqIN19d")
        self.scraper = EnergyPriceScraper()

    def update_country_energy_data(self, country_name="IT"):
        """Obtiene datos desde la API y actualiza la BD."""
        consumption_data, production_data = self.api_client.get_energy_mix(country_name)

        if not consumption_data or not production_data:
            return "Error: No se pudieron obtener datos de la API."

        country = Country(country_name)
        country.set_energy_data(EnergyMix(**consumption_data), EnergyMix(**production_data))

        query = """
        INSERT INTO energy_consumption 
        (zone, datetime, nuclear, geothermal, biomass, coal, wind, solar, hydro, gas, oil, unknown, "hydro discharge", "battery discharge")
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = tuple(country.energy_consumption.to_dict().values())
        self.db.execute_query(query, params)

        return f"Datos de {country_name} actualizados en la base de datos."

    def update_energy_prices(self):
        """Ejecuta el scraper para obtener precios de energía y guardarlos en CSV."""
        self.scraper.scrape_prices()
        return "Precios de electricidad actualizados en 'data/electricity_prices.csv'."
