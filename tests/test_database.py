import pytest
import sqlite3
from backend.database import DatabaseManager
from backend.models import EnergyMix

@pytest.fixture
def db():
    """Crea una base de datos persistente para pruebas y limpia después de cada test."""
    db = DatabaseManager("data/bd_energy.db")  # Usamos la base de datos real

    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS energy_consumption (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone TEXT,
                datetime TEXT,
                nuclear INTEGER,
                geothermal INTEGER DEFAULT 0,
                biomass INTEGER DEFAULT 0,
                coal INTEGER DEFAULT 0,
                wind INTEGER DEFAULT 0,
                solar INTEGER DEFAULT 0,
                hydro INTEGER DEFAULT 0,
                gas INTEGER DEFAULT 0,
                oil INTEGER DEFAULT 0,
                unknown INTEGER DEFAULT 0,
                hydro_discharge INTEGER DEFAULT 0,
                battery_discharge INTEGER DEFAULT 0
            )
        """)
        conn.commit()

    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM energy_consumption;")  # Limpia la tabla antes de cada test
        conn.commit()

    yield db  # Devuelve la BD para los tests

def test_insert_and_fetch_data(db):
    """Prueba que los datos se insertan y se recuperan correctamente como objetos."""
    
    energy_mix = EnergyMix(
        zone="IT", datetime="2025-03-10T16:00:00.000Z", nuclear=2000, geothermal=100, solar=500
    )

    db.execute_query("""
        INSERT INTO energy_consumption 
        (zone, datetime, nuclear, geothermal, solar) 
        VALUES (?, ?, ?, ?, ?)
    """, (energy_mix.zone, energy_mix.datetime, energy_mix.nuclear, energy_mix.geothermal, energy_mix.solar))

    results = db.fetch_energy_consumption()  # Ahora devuelve objetos EnergyMix

    assert len(results) == 1
    assert isinstance(results[0], EnergyMix)
    assert results[0].zone == "IT"
    assert results[0].datetime == "2025-03-10T16:00:00.000Z"
    assert results[0].nuclear == 2000
    assert results[0].geothermal == 100
    assert results[0].solar == 500
