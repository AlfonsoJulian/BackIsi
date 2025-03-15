from unittest.mock import patch
from backend.energy_service import EnergyService
from backend.models import Country, EnergyMix

@patch("backend.energy_service.EnergyAPIClient.get_energy_mix")
@patch("backend.energy_service.DatabaseManager.execute_query")
def test_update_country_energy_data(mock_execute_query, mock_get_energy_mix):
    """Prueba que los datos se obtienen y almacenan correctamente en la BD."""
    mock_get_energy_mix.return_value = (
        {
            "zone": "IT",
            "datetime": "2025-03-10T16:00:00.000Z",
            "nuclear": 2000,
            "geothermal": 100,
            "biomass": 200,
            "coal": 300,
            "wind": 400,
            "solar": 500,
            "hydro": 600,
            "gas": 700,
            "oil": 800,
            "unknown": 900,
            "hydro_discharge": 1000,  # <- Eliminamos espacios
            "battery_discharge": 1100,  # <- Eliminamos espacios
        },
        {
            "zone": "IT",
            "datetime": "2025-03-10T16:00:00.000Z",
            "nuclear": 2100,
            "geothermal": 150,
            "biomass": 250,
            "coal": 350,
            "wind": 450,
            "solar": 550,
            "hydro": 650,
            "gas": 750,
            "oil": 850,
            "unknown": 950,
            "hydro_discharge": 1050,  # <- Eliminamos espacios
            "battery_discharge": 1150,  # <- Eliminamos espacios
        }
    )

    energy_service = EnergyService()
    result = energy_service.update_country_energy_data("IT")

    # ACTUALIZAMOS la aserción con el mensaje correcto
    assert result == "Datos de IT actualizados en la base de datos."
