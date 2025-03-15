from unittest.mock import patch, call
import pytest
from backend.energy_service import EnergyService
from backend.models import EnergyMix


@pytest.fixture
def energy_service():
    return EnergyService()

@patch("backend.energy_service.EnergyAPIClient.get_energy_mix")
@patch("backend.energy_service.DatabaseManager.execute_query")
def test_update_country_energy_data(mock_execute_query, mock_get_energy_mix, energy_service):
    """Prueba que los datos se obtienen y almacenan correctamente en la BD como objetos."""
    
    # Simulamos la respuesta de la API devolviendo objetos EnergyMix
    mock_get_energy_mix.return_value = (
        EnergyMix(
            zone="IT", datetime="2025-03-10T16:00:00.000Z", nuclear=2000, geothermal=100, biomass=200,
            coal=300, wind=400, solar=500, hydro=600, gas=700, oil=800, unknown=900,
            hydro_discharge=1000, battery_discharge=1100
        ),
        EnergyMix(
            zone="IT", datetime="2025-03-10T16:00:00.000Z", nuclear=2100, geothermal=150, biomass=250,
            coal=350, wind=450, solar=550, hydro=650, gas=750, oil=850, unknown=950,
            hydro_discharge=1050, battery_discharge=1150
        )
    )

    result = energy_service.update_country_energy_data("IT")

    assert result == "Datos de IT actualizados en la base de datos."

    expected_consumption_values = mock_get_energy_mix.return_value[0].to_tuple()
    expected_production_values = mock_get_energy_mix.return_value[1].to_tuple()

    # 🔍 **Depuración: Ver qué valores se están insertando realmente**
    print("\n🔍 Valores esperados para consumo:", expected_consumption_values)
    print("\n🔍 Valores esperados para producción:", expected_production_values)
    print("\n🔍 Valores insertados realmente:", mock_execute_query.call_args_list)

    # ✅ **Verificar que se insertaron los datos en algún momento, sin importar el orden**
    execute_calls = [
        call(
            "INSERT INTO energy_consumption (zone, datetime, nuclear, geothermal, biomass, coal, wind, solar, hydro, gas, oil, unknown, hydro_discharge, battery_discharge) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            expected_consumption_values
        ),
        call(
            "INSERT INTO energy_production (zone, datetime, nuclear, geothermal, biomass, coal, wind, solar, hydro, gas, oil, unknown, hydro_discharge, battery_discharge) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            expected_production_values
        ),
    ]


    print("\n🔍 Valores esperados (expected_consumption_values):", expected_consumption_values)
    print("\n🔍 Valores esperados (expected_production_values):", expected_production_values)

    # Permitir que las llamadas ocurran en cualquier orden
    mock_execute_query.assert_has_calls(execute_calls, any_order=True)
