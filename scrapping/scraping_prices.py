import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

class EnergyPriceScraper:
    URL_MAIN = "https://datosmacro.expansion.com/energia-y-medio-ambiente/electricidad-precio-hogares"
    BASE_URL = "https://datosmacro.expansion.com"

    def __init__(self):
        self.country_links = set()

    def get_country_links(self):
        """Obtiene los enlaces de cada país en la página principal."""
        response = requests.get(self.URL_MAIN)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/energia-y-medio-ambiente/electricidad-precio-hogares/") and href != "/energia-y-medio-ambiente/electricidad-precio-hogares":
                self.country_links.add(self.BASE_URL + href)

        return self.country_links

    def scrape_prices(self):
        """Extrae precios de electricidad y los guarda en un CSV."""
        dataframes = []
        for url in self.get_country_links():
            try:
                print(f"Scrapeando: {url}")
                res = requests.get(url)
                res.raise_for_status()
                time.sleep(1)

                soup_country = BeautifulSoup(res.text, "html.parser")
                table = soup_country.find("table", id="tb0")
                if table:
                    df = pd.read_html(str(table))[0]
                    country_name = url.split("/")[-1].replace("-", " ").title()
                    df["País"] = country_name
                    dataframes.append(df)
            except Exception as e:
                print(f"Error en {url}: {e}")

        if dataframes:
            df_total = pd.concat(dataframes, ignore_index=True)
            df_total.to_csv("data/electricity_prices.csv", index=False)
            print("Archivo CSV guardado en 'data/electricity_prices.csv'.")

