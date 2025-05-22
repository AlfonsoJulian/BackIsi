from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decimal import Decimal       # <— Asegúrate de tener esto
import os, re, runpy

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'backend', 'bd', 'energy.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# de MWh a PJ y pa' anualizar
MWH_TO_PJ    = 3.6e-6
HOUR_TO_YEAR = 24 * 365


class HistoricoPrecio(db.Model):
    __tablename__ = 'historico_precio'
    __table_args__ = {'extend_existing': True}

    pais               = db.Column(db.Text, db.ForeignKey('pais.pais'), primary_key=True)
    anio               = db.Column(db.Integer, primary_key=True)
    precio_kw_impuesto = db.Column(db.Numeric(20, 8))
    precio_kw          = db.Column(db.Numeric(20, 8))

    pais_obj = db.relationship('Pais', backref='historico_precio')


# --- Ajuste en Pais: añadir relación al nuevo modelo ---
class Pais(db.Model):
    __tablename__ = 'pais'
    __table_args__ = {'extend_existing': True}

    pais             = db.Column(db.Text, primary_key=True)
    pib_anual        = db.Column(db.Text)
    pib_per_capita   = db.Column(db.Text)
    co2_per_capita   = db.Column(db.Text)

    consumos         = db.relationship('ActualConsumoProduccion', backref='pais_obj')
    historicos       = db.relationship('HistoricoConsumoProduccion', backref='pais_obj')
    precios_historico = db.relationship('HistoricoPrecio', backref='pais_obj')

class ActualConsumoProduccion(db.Model):
    __tablename__ = 'actual_consumo_produccion'
    __table_args__ = {'extend_existing': True}
    pais                 = db.Column(db.Text, db.ForeignKey('pais.pais'), primary_key=True)
    indicador            = db.Column(db.Text, primary_key=True)
    fecha                = db.Column(db.Text, primary_key=True)
    coal_peat_oil_shale  = db.Column(db.Text)
    natural_gas          = db.Column(db.Text)
    nuclear              = db.Column(db.Text)
    oil_products         = db.Column(db.Text)
    renewables_and_waste = db.Column(db.Text)
    total                = db.Column(db.Text)

class HistoricoConsumoProduccion(db.Model):
    __tablename__ = 'historico_consumo_produccion'
    __table_args__ = {'extend_existing': True}
    pais                 = db.Column(db.Text, db.ForeignKey('pais.pais'), primary_key=True)
    indicador            = db.Column(db.Text, primary_key=True)
    anio                 = db.Column(db.Integer, primary_key=True)
    coal_peat_oil_shale  = db.Column(db.Text)
    natural_gas          = db.Column(db.Text)
    nuclear              = db.Column(db.Text)
    oil_products         = db.Column(db.Text)
    renewables_and_waste = db.Column(db.Text)
    total                = db.Column(db.Text)

# --- UTILIDADES ---
def safe_float(value):
    if value in (None, '', 'NULL'):
        return 0.0
    try:
        return float(value)
    except:
        return 0.0

def parse_date_safe(date_str):
    if not date_str:
        return None
    if isinstance(date_str, str) and date_str.endswith('Z'):
        date_str = date_str[:-1]
    for fmt in ('%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

def get_year_from_date(date_value):
    if hasattr(date_value, 'year'):
        return date_value.year
    return None

def to_camel_case(s: str) -> str:
    parts = re.findall(r'[A-Za-z0-9]+', s)
    parts = [p.lower() for p in parts]
    return parts[0] + ''.join(p.title() for p in parts[1:]) if parts else ''

# --- RUTAS PRINCIPALES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consumo', methods=['GET','POST'])
def show_consumption():
    try:
        paises = [p.pais for p in Pais.query.order_by(Pais.pais).all()]
        indicadores = [i[0] for i in db.session.query(
                           ActualConsumoProduccion.indicador
                       ).distinct().order_by(ActualConsumoProduccion.indicador).all()]
        anios = [y[0] for y in db.session.query(
                     HistoricoConsumoProduccion.anio
                 ).distinct().order_by(HistoricoConsumoProduccion.anio).all()]

        with db.session.no_autoflush:
            actual_list = ActualConsumoProduccion.query.order_by(
                              ActualConsumoProduccion.pais,
                              ActualConsumoProduccion.indicador,
                              ActualConsumoProduccion.fecha
                          ).all()
            for a in actual_list:
                a.fecha_parsed = parse_date_safe(a.fecha)

        historico_list = HistoricoConsumoProduccion.query.order_by(
                             HistoricoConsumoProduccion.pais,
                             HistoricoConsumoProduccion.indicador,
                             HistoricoConsumoProduccion.anio
                         ).all()
    except Exception as e:
        return f"<h1>Error cargando datos:</h1><p>{e}</p>"

    datos = None
    if request.method == 'POST':
        pais_sel = request.form.get('pais')
        ind_sel  = request.form.get('indicador')
        anio_sel = request.form.get('anio', type=int)
        if pais_sel and ind_sel:
            try:
                actual = (ActualConsumoProduccion.query
                          .filter_by(pais=pais_sel, indicador=ind_sel)
                          .order_by(ActualConsumoProduccion.fecha.desc())
                          .first())
                if actual:
                    fecha_parseada = parse_date_safe(actual.fecha) or actual.fecha
                    year = get_year_from_date(fecha_parseada) or get_year_from_date(actual.fecha)
                    target_year = anio_sel or year

                    historico = HistoricoConsumoProduccion.query.filter_by(
                        pais=pais_sel,
                        indicador=ind_sel,
                        anio=target_year
                    ).first()

                    datos = {
                        'pais': pais_sel,
                        'indicador': ind_sel,
                        'fecha_actual': fecha_parseada,
                        'valores_actual': {
                            'coal': safe_float(actual.coal_peat_oil_shale),
                            'gas':  safe_float(actual.natural_gas),
                            'nuclear': safe_float(actual.nuclear),
                            'oil': safe_float(actual.oil_products),
                            'renwaste': safe_float(actual.renewables_and_waste),
                            'total': safe_float(actual.total),
                        },
                        'valores_historico': None,
                    }
                    if historico:
                        datos['valores_historico'] = {
                            'coal': safe_float(historico.coal_peat_oil_shale),
                            'gas':  safe_float(historico.natural_gas),
                            'nuclear': safe_float(historico.nuclear),
                            'oil': safe_float(historico.oil_products),
                            'renwaste': safe_float(historico.renewables_and_waste),
                            'total': safe_float(historico.total),
                        }
            except Exception as e:
                datos = {'error': str(e)}

    return render_template(
        'consumo_comparador.html',
        paises=paises,
        indicadores=indicadores,
        anios=anios,
        actual_list=actual_list,
        historico_list=historico_list,
        datos=datos
    )


# --- NUEVA RUTA: ACTUALIZAR DATOS EN BD LLAMANDO DIRECTO AL SCRIPT ---
@app.route('/update_consumo')
def update_consumo():
    # ruta absoluta a tu script
    script_path = r'C:\Users\Usuario\Desktop\facultad\cuarto\2CUATRI\isi\practicas\BackIsi\backend\scrapping\api_mix.py'
    try:
        # ejecuta el script en el mismo proceso/Python
        runpy.run_path(script_path, run_name="__main__")
    except Exception as e:
        return f"<h3>Error al actualizar:</h3><pre>{e}</pre>", 500

    return "<h3>Datos actualizados correctamente llamando a api_mix.py.</h3>"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
