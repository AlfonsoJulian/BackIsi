import requests

# URL de la API
url = "https://api.electricitymap.org/v3/power-breakdown/latest?zone=IT"

# Cabecera con el token de autenticación
headers = {
    "auth-token": "UaBrRwos3WkWtvqIN19d"
}

# Realiza la solicitud GET a la API
response = requests.get(url, headers=headers)

# Muestra la respuesta completa en formato de texto
print(response.text)
