import pytest
import requests
from unittest.mock import patch
from scrapping.api_client import EnergyAPIClient
from backend.models import EnergyMix

@pytest.fixture
def api_client():
    return EnergyAPIClient(auth_token="test_token")

@patch("requests.get")
def test_get_energy_mix_success(mock_get, api_client):
    """Prueba que la API devuelve datos correctamente y se convierte en objetos EnergyMix."""
    mock_response = {
        "zone": "IT",
        "datetime": "2025-03-10T16:00:00.000Z",
        "powerConsumptionBreakdown": {"nuclear": 2000, "solar": 500},
        "powerProductionBreakdown": {"nuclear": 2100, "solar": 600}
    }
    
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    consumption, production = api_client.get_energy_mix("IT")

    assert isinstance(consumption, EnergyMix)
    assert isinstance(production, EnergyMix)
    assert consumption.nuclear == 2000
    assert consumption.solar == 500
    assert production.nuclear == 2100
    assert production.solar == 600

@patch("requests.get")
def test_get_energy_mix_failure(mock_get, api_client):
    """Prueba que la API maneja errores correctamente y devuelve None."""
    mock_get.return_value.status_code = 500

    consumption, production = api_client.get_energy_mix("IT")

    assert consumption is None
    assert production is None
