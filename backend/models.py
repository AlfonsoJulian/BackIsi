from datetime import datetime

class EnergyMix:
    """Representa la mezcla energética de una zona específica."""
    def __init__(self, zone, datetime, nuclear=0, geothermal=0, biomass=0, coal=0, wind=0, solar=0, 
                 hydro=0, gas=0, oil=0, unknown=0, hydro_discharge=0, battery_discharge=0):
        self.zone = zone
        self.datetime = datetime if isinstance(datetime, str) else datetime.isoformat()
        self.nuclear = nuclear
        self.geothermal = geothermal
        self.biomass = biomass
        self.coal = coal
        self.wind = wind
        self.solar = solar
        self.hydro = hydro
        self.gas = gas
        self.oil = oil
        self.unknown = unknown
        self.hydro_discharge = hydro_discharge
        self.battery_discharge = battery_discharge

    def to_tuple(self):
        """Convierte la instancia en una tupla lista para insertar en la BD."""
        return (self.zone, self.datetime, self.nuclear, self.geothermal, self.biomass, self.coal,
                self.wind, self.solar, self.hydro, self.gas, self.oil, self.unknown,
                self.hydro_discharge, self.battery_discharge)

class Country:
    """Representa un país con su consumo y producción energética."""
    def __init__(self, name):
        self.name = name
        self.consumption = None
        self.production = None

    def set_energy_data(self, consumption: EnergyMix, production: EnergyMix):
        """Asigna datos de consumo y producción a la instancia del país."""
        self.consumption = consumption
        self.production = production
