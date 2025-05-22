from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bd_energy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Modelos ORM ---
class Pais(db.Model):
    __tablename__ = 'pais'
    pais = db.Column(db.Text, primary_key=True)
    pib_anual = db.Column(db.Numeric(20,8))
    pib_per_capita = db.Column(db.Numeric(20,8))
    co2_per_capita = db.Column(db.Numeric(20,8))
    consumos = db.relationship('ActualConsumoProduccion', backref='pais_obj')
    historicos = db.relationship('HistoricoConsumoProduccion', backref='pais_obj')

class ActualConsumoProduccion(db.Model):
    __tablename__ = 'actual_consumo_produccion'
    pais = db.Column(db.Text, db.ForeignKey('pais.pais'), primary_key=True)
    indicador = db.Column(db.Text, primary_key=True)
    fecha = db.Column(db.Date, primary_key=True)
    coal_peat_oil_shale  = db.Column(db.Numeric(20,8))
    natural_gas          = db.Column(db.Numeric(20,8))
    nuclear              = db.Column(db.Numeric(20,8))
    oil_products         = db.Column(db.Numeric(20,8))
    renewables_and_waste = db.Column(db.Numeric(20,8))
    total                = db.Column(db.Numeric(20,8))

class HistoricoConsumoProduccion(db.Model):
    __tablename__ = 'historico_consumo_produccion'
    pais = db.Column(db.Text, db.ForeignKey('pais.pais'), primary_key=True)
    indicador = db.Column(db.Text, primary_key=True)
    anio = db.Column(db.Integer, primary_key=True)
    coal_peat_oil_shale  = db.Column(db.Numeric(20,8))
    natural_gas          = db.Column(db.Numeric(20,8))
    nuclear              = db.Column(db.Numeric(20,8))
    oil_products         = db.Column(db.Numeric(20,8))
    renewables_and_waste = db.Column(db.Numeric(20,8))
    total                = db.Column(db.Numeric(20,8))

# --- Rutas ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consumo', methods=['GET','POST'])
def show_consumption():
    # 1) obtener lista de países e indicadores para el formulario
    paises = [p.pais for p in Pais.query.order_by(Pais.pais).all()]
    indicadores = db.session.query(ActualConsumoProduccion.indicador)\
                            .distinct().order_by(ActualConsumoProduccion.indicador).all()
    indicadores = [i[0] for i in indicadores]

    datos = None
    if request.method == 'POST':
        pais_sel = request.form['pais']
        ind_sel  = request.form['indicador']

        # 2) consumo actual: última fecha disponible
        actual = ActualConsumoProduccion.query\
            .filter_by(pais=pais_sel, indicador=ind_sel)\
            .order_by(ActualConsumoProduccion.fecha.desc())\
            .first()

        if actual:
            year = actual.fecha.year
            # 3) histórico para ese año
            historico = HistoricoConsumoProduccion.query\
                .filter_by(pais=pais_sel, indicador=ind_sel, anio=year)\
                .first()

            datos = {
                'pais': pais_sel,
                'indicador': ind_sel,
                'fecha_actual': actual.fecha,
                'valores_actual': {
                    'coal': actual.coal_peat_oil_shale,
                    'gas': actual.natural_gas,
                    'nuclear': actual.nuclear,
                    'oil': actual.oil_products,
                    'renwaste': actual.renewables_and_waste,
                    'total': actual.total,
                },
                'valores_historico': None,
            }
            if historico:
                datos['valores_historico'] = {
                    'coal': historico.coal_peat_oil_shale,
                    'gas': historico.natural_gas,
                    'nuclear': historico.nuclear,
                    'oil': historico.oil_products,
                    'renwaste': historico.renewables_and_waste,
                    'total': historico.total,
                }

    return render_template('consumo_comparador.html',
                           paises=paises,
                           indicadores=indicadores,
                           datos=datos)


if __name__ == "__main__":
    # Crea las tablas si no existen
    with app.app_context():
        db.create_all()
    app.run(debug=True)
