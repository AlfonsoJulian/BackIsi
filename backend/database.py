import sqlite3

class DatabaseManager:
    def __init__(self, db_name="data/bd_energy.db"):
        self.db_name = db_name

    def execute_query(self, query, params=()):
        """Ejecuta una consulta en la base de datos (INSERT, UPDATE, DELETE)."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # 🔥 Debug: Mostrar las tablas en la base de datos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tablas en la BD {self.db_name}: {tables}")  # << Verificar si la tabla está creada

        cursor.execute(query, params)
        conn.commit()
        conn.close()
    
    def fetch_all(self, query):
        """Ejecuta una consulta SELECT y devuelve todos los resultados."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
