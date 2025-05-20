import sqlite3

# Conecta (o crea) la base de datos
conn = sqlite3.connect('energy.db')
cur = conn.cursor()

# Habilita el uso de claves foráneas
cur.execute('PRAGMA foreign_keys = ON;')

# --- TABLA PAIS ---
cur.execute('''
CREATE TABLE IF NOT EXISTS pais (
    pais               TEXT        PRIMARY KEY,
    pib_anual          DECIMAL(20,8),
    pib_per_capita     DECIMAL(20,8),
    co2_per_capita     DECIMAL(20,8)
);
''')

# --- TABLA HISTORICO_PRECIO ---
cur.execute('''
CREATE TABLE IF NOT EXISTS historico_precio (
    pais                 TEXT,
    anio                 INTEGER,
    precio_kw_impuesto   DECIMAL(20,8),
    precio_kw            DECIMAL(20,8),
    PRIMARY KEY(pais, anio),
    FOREIGN KEY(pais) REFERENCES pais(pais)
);
''')

# --- TABLA HISTORICO_CONSUMO_PRODUCCION ---
cur.execute('''
CREATE TABLE IF NOT EXISTS historico_consumo_produccion (
    pais                   TEXT,
    indicador              TEXT,
    anio                   INTEGER,
    coal_peat_oil_shale    DECIMAL(20,8),
    natural_gas            DECIMAL(20,8),
    nuclear                DECIMAL(20,8),
    oil_products           DECIMAL(20,8),
    renewables_and_waste   DECIMAL(20,8),
    total                  DECIMAL(20,8),
    PRIMARY KEY(pais, indicador, anio),
    FOREIGN KEY(pais) REFERENCES pais(pais)
);
''')

# --- TABLA ACTUAL_CONSUMO_PRODUCCION ---
cur.execute('''
CREATE TABLE IF NOT EXISTS actual_consumo_produccion (
    pais                   TEXT,
    indicador              TEXT,
    fecha                  DATE,
    coal_peat_oil_shale    DECIMAL(20,8),
    natural_gas            DECIMAL(20,8),
    nuclear                DECIMAL(20,8),
    oil_products           DECIMAL(20,8),
    renewables_and_waste   DECIMAL(20,8),
    total                  DECIMAL(20,8),
    PRIMARY KEY(pais, indicador, fecha),
    FOREIGN KEY(pais) REFERENCES pais(pais)
);
''')

# Confirmación
conn.commit()
print("Base de datos 'energy.db' creada con tablas y precisión ampliada a 8 decimales.")
conn.close()
