import pytest
import sqlite3
from backend.database import DatabaseManager

@pytest.fixture
def db():
    """Crea una base de datos persistente para pruebas y limpia después de cada test."""
    db = DatabaseManager("data/bd_energy.db")  # Usamos la base de datos real

    # 🔥 Asegurar que la tabla existe antes del test
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

    # 🔥 **Limpiar los datos antes de cada test**
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM energy_consumption;")  # Eliminar datos previos
        conn.commit()

    yield db  # Pasar la BD al test

def test_insert_and_fetch_data(db):
    """Prueba que los datos se insertan y se recuperan correctamente."""
    db.execute_query("""
        INSERT INTO energy_consumption (zone, datetime, nuclear, solar)
        VALUES (?, ?, ?, ?)
    """, ("IT", "2025-03-10T16:00:00.000Z", 2000, 500))

    results = db.fetch_all("SELECT * FROM energy_consumption")

    # 🔥 **Debugging**
    print(f"Resultados en la BD: {results}")  # Para ver los datos insertados

    assert len(results) == 1  # Ahora debería haber solo un registro
    assert results[0][1] == "IT"
    assert results[0][2] == "2025-03-10T16:00:00.000Z"
    assert results[0][3] == 2000
    assert results[0][8] == 500  # `solar` está en la columna 8
