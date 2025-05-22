from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from decimal import Decimal
import os, re, runpy
from flask import abort


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'backend', 'bd', 'energy.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# de MWh a PJ y pa' anualizar
MWH_TO_PJ    = 3.6e-6
HOUR_TO_YEAR = 24 * 365

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

# --- MODELOS ---
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

    # Atributos de simulador (no persistidos)
    _datacenters_owned = 0
    _powerplants_owned = 0

    def buy_datacenters(self, count: int, year: int, capacity_kw: Decimal) -> Decimal:
        """Compra datacenters usando precio histórico sin impuesto."""
        record = next((hp for hp in self.precios_historico if hp.anio == year), None)
        if not record:
            raise ValueError(f'No hay precio histórico para {self.pais} en {year}')
        cost = record.precio_kw * capacity_kw * count
        self._datacenters_owned += count
        return cost

    def buy_powerplants(self, count: int, year: int, capacity_kw: Decimal) -> Decimal:
        """Compra centrales usando precio con impuesto."""
        record = next((hp for hp in self.precios_historico if hp.anio == year), None)
        if not record:
            raise ValueError(f'No hay precio histórico para {self.pais} en {year}')
        cost = record.precio_kw_impuesto * capacity_kw * count
        self._powerplants_owned += count
        return cost

    def simulate_energy_impact(self) -> dict:
        """Calcula consumo y producción anual en MWh y PJ."""
        # Consumo DC (kW→kWh→MWh)
        annual_dc_mwh = (self._datacenters_owned *
                         getattr(self, '_dc_capacity_kw', 0) *
                         HOUR_TO_YEAR) / 1000
        # Producción PP (kW→kWh→MWh)
        annual_pp_mwh = (self._powerplants_owned *
                         getattr(self, '_pp_capacity_kw', 0) *
                         HOUR_TO_YEAR) / 1000
        net_mwh = annual_pp_mwh - annual_dc_mwh
        return {
            'datacenters_mwh': annual_dc_mwh,
            'powerplants_mwh': annual_pp_mwh,
            'net_mwh': net_mwh,
            'net_pj': net_mwh * MWH_TO_PJ
        }

    def record_simulation(self, indicador: str) -> 'ActualConsumoProduccion':
        """Guarda resultado neto en actual_consumo_produccion."""
        impact = self.simulate_energy_impact()
        today = date.today()
        total = Decimal(str(impact['net_mwh']))
        # Crear o actualizar registro
        actual = ActualConsumoProduccion.query.get((self.pais, indicador, today.isoformat()))
        if not actual:
            actual = ActualConsumoProduccion(
                pais=self.pais,
                indicador=indicador,
                fecha=today.isoformat(),
                coal_peat_oil_shale='0',
                natural_gas='0',
                nuclear='0',
                oil_products='0',
                renewables_and_waste='0',
                total=str(total)
            )
            db.session.add(actual)
        else:
            actual.total = str(total)
        db.session.commit()
        return actual


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


class HistoricoPrecio(db.Model):
    __tablename__ = 'historico_precio'
    __table_args__ = {'extend_existing': True}

    pais               = db.Column(db.Text, db.ForeignKey('pais.pais'), primary_key=True)
    anio               = db.Column(db.Integer, primary_key=True)
    precio_kw_impuesto = db.Column(db.Numeric(20, 8))
    precio_kw          = db.Column(db.Numeric(20, 8))
    # <-- aquí NO definimos otro relationship; lo hereda de Pais.precios_historico

# --- RUTAS PRINCIPALES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consumo', methods=['GET','POST'])
def show_consumption():
    try:
        paises = [p.pais for p in Pais.query.order_by(Pais.pais)]
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

@app.route('/simulador')
def simulador():
    paises = [p.pais for p in Pais.query.order_by(Pais.pais)]
    return render_template('simulador.html', paises=paises)

# --- RUTA PARA ACTUALIZAR CONSCRONÍA ---
@app.route('/update_consumo')
def update_consumo():
    script_path = r'C:\Users\Usuario\Desktop\facultad\cuarto\2CUATRI\isi\practicas\BackIsi\backend\scrapping\api_mix.py'
    try:
        runpy.run_path(script_path, run_name="__main__")
    except Exception as e:
        return f"<h3>Error al actualizar:</h3><pre>{e}</pre>", 500
    return "<h3>Datos actualizados correctamente llamando a api_mix.py.</h3>"


@app.route('/api/simulate', methods=['POST'])
def simulate_route():
    p = request.get_json(force=True)
    pais_key = p.get('pais')
    year     = p.get('year')
    dc       = int(p.get('datacenters',  0))
    dc_kw    = Decimal(str(p.get('dc_capacity_kw', 0)))
    pp       = int(p.get('powerplants',  0))
    pp_kw    = Decimal(str(p.get('pp_capacity_kw', 0)))
    record   = p.get('record', False)
    indicator= p.get('indicator', 'simulacion')

    # 1) Leer país y precio histórico
    pais   = db.session.get(Pais, pais_key) or abort(404, f'País "{pais_key}" no existe')
    precio = (HistoricoPrecio
              .query
              .filter_by(pais=pais_key, anio=year)
              .first()) or abort(400, f'No hay precio para {year}')

    # 2) Calcular costes
    cost_dc = precio.precio_kw          * dc_kw * dc
    cost_pp = precio.precio_kw_impuesto * pp_kw * pp

    # 3) Calcular impacto en MWh y PJ
    cons_mwh = dc_kw * dc * HOUR_TO_YEAR / Decimal(1000)
    prod_mwh = pp_kw * pp * HOUR_TO_YEAR / Decimal(1000)
    net_mwh  = prod_mwh - cons_mwh
    net_pj   = net_mwh * Decimal(str(MWH_TO_PJ))

    result = {
        'coste_datacenters': float(cost_dc),
        'coste_powerplants': float(cost_pp),
        'impact': {
            'datacenters_mwh':  float(cons_mwh),
            'powerplants_mwh':  float(prod_mwh),
            'net_mwh':          float(net_mwh),
            'net_pj':           float(net_pj)
        }
    }

    # 4) (Opcional) Grabar en BD
    if record:
        act = ActualConsumoProduccion(
            pais=pais_key,
            indicador=indicator,
            fecha=date.today().isoformat(),
            coal_peat_oil_shale='0',
            natural_gas='0',
            nuclear='0',
            oil_products='0',
            renewables_and_waste='0',
            total=str(net_mwh)
        )
        db.session.add(act)
        db.session.commit()
        result['record'] = {
            'fecha':     act.fecha,
            'total_mwh': float(act.total)
        }

    return jsonify(result)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
