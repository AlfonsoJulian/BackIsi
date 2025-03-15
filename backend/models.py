class EnergyMix:
    def __init__(self, zone, datetime, nuclear, geothermal, biomass, coal, wind, solar, hydro, gas, oil, unknown, hydro_discharge, battery_discharge):
        self.zone = zone
        self.datetime = datetime
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

    def to_dict(self):
        return self.__dict__

class Country:
    def __init__(self, name):
        self.name = name
        self.energy_consumption = None
        self.energy_production = None

    def set_energy_data(self, consumption, production):
        self.energy_consumption = consumption
        self.energy_production = production
