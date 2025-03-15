from flask import Blueprint, render_template, request
from backend.database import DatabaseManager
from backend.energy_service import EnergyService

routes = Blueprint('routes', __name__)  # Asegurar que el nombre es 'routes'

db = DatabaseManager()
energy_service = EnergyService()

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/show_consumption')
def show_consumption():
    db.execute_query("VACUUM")  # Optimiza la base de datos
    consumption_data = db.fetch_all("SELECT * FROM energy_consumption ORDER BY datetime DESC LIMIT 20")
    return render_template('show_consumption.html', consumption_data=consumption_data)

@routes.route('/show_production')
def show_production():
    db.execute_query("VACUUM")
    production_data = db.fetch_all("SELECT * FROM energy_production ORDER BY datetime DESC LIMIT 20")
    return render_template('show_production.html', production_data=production_data)

@routes.route('/update_data', methods=['POST'])
def update_data():
    return energy_service.update_country_energy_data("IT")

@routes.route('/update_prices', methods=['POST'])
def update_prices():
    """Llama a EnergyService para actualizar los precios de electricidad."""
    return energy_service.update_energy_prices()
