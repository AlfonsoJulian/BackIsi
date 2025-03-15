from backend.models import EnergyMix
import sqlite3

class DatabaseManager:
    """Clase para interactuar con la base de datos SQLite."""
    def __init__(self, db_name="data/bd_energy.db"):
        self.db_name = db_name

    def execute_query(self, query, params=()):
        """Ejecuta consultas de modificación (INSERT, UPDATE, DELETE)."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def fetch_all(self, query, params=()):
        """Ejecuta consultas SELECT y devuelve el resultado."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results

    def fetch_energy_consumption(self):
        """Recupera datos de la BD y los devuelve como objetos EnergyMix."""
        query = "SELECT zone, datetime, nuclear, geothermal, biomass, coal, wind, solar, hydro, gas, oil, unknown, hydro_discharge, battery_discharge FROM energy_consumption"
        results = self.fetch_all(query)
        return [EnergyMix(*row) for row in results]  # Ahora excluye la columna `id`
