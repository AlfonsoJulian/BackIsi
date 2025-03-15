import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# URL principal de precios de electricidad en hogares
url_main = "https://datosmacro.expansion.com/energia-y-medio-ambiente/electricidad-precio-hogares"
base_url = "https://datosmacro.expansion.com"

# Realizamos la petición a la página principal
response = requests.get(url_main)
response.raise_for_status()

# Parseamos el HTML con BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Extraemos los enlaces de los países
country_links = set()
for a in soup.find_all("a", href=True):
    href = a["href"]
    # Filtrar enlaces que comiencen con la ruta de precios para países, descartando la propia página principal
    if href.startswith("/energia-y-medio-ambiente/electricidad-precio-hogares/") and href != "/energia-y-medio-ambiente/electricidad-precio-hogares":
        full_url = base_url + href
        country_links.add(full_url)

print("Enlaces de países encontrados:")
for link in country_links:
    print(link)

# Lista para almacenar los DataFrames de cada país
dataframes = []

# Recorrer cada enlace de país
for url in country_links:
    try:
        print(f"\nProcesando: {url}")
        res = requests.get(url)
        res.raise_for_status()
        time.sleep(1)  # Para evitar sobrecargar el servidor
        
        # Parseamos la página del país
        soup_country = BeautifulSoup(res.text, "html.parser")
        
        # Buscamos la tabla principal con id "tb0"
        table = soup_country.find("table", id="tb0")
        if table:
            df = pd.read_html(str(table))[0]
            # Extraemos el nombre del país desde la URL (última parte, formateada)
            country_name = url.split("/")[-1].replace("-", " ").title()
            df["País"] = country_name
            dataframes.append(df)
            print(f"Tabla extraída para: {country_name}")
        else:
            print("No se encontró la tabla con id 'tb0' en la página.")
    except Exception as e:
        print(f"Error al procesar {url}: {e}")

# Combinar todas las tablas y guardar en un CSV
if dataframes:
    df_total = pd.concat(dataframes, ignore_index=True)
    df_total.to_csv("electricity_prices.csv", index=False)
    print("\nEl archivo CSV se ha guardado como 'electricity_prices.csv'")
else:
    print("No se encontraron datos para guardar.")
