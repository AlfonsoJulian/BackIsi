import pandas as pd
import sqlite3

conn = sqlite3.connect("bd_energy.db")

print("📊 Tabla 'energia':")
df_energia = pd.read_sql("SELECT * FROM energia LIMIT 10", conn)
print(df_energia)

print("\n📊 Tabla 'precios':")
df_precios = pd.read_sql("SELECT * FROM precios LIMIT 10", conn)
print(df_precios)

conn.close()
