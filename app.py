from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
# CORREGIDO: Usar ruta absoluta para evitar problemas de permisos
import os
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'backend', 'bd', 'energy.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Modelos ORM FORZANDO Text ---
class Pais(db.Model):
    __tablename__ = 'pais'
    __table_args__ = {'extend_existing': True}  # CLAVE: Fuerza a redefinir la tabla
    
    pais = db.Column(db.Text, primary_key=True)
    # FORZAMOS a Text para evitar conversión automática
    pib_anual = db.Column(db.Text)  
    pib_per_capita = db.Column(db.Text)  
    co2_per_capita = db.Column(db.Text)  
    consumos = db.relationship('ActualConsumoProduccion', backref='pais_obj')
    historicos = db.relationship('HistoricoConsumoProduccion', backref='pais_obj')

class ActualConsumoProduccion(db.Model):
    __tablename__ = 'actual_consumo_produccion'
    __table_args__ = {'extend_existing': True}  # CLAVE: Fuerza a redefinir la tabla
    
    pais = db.Column(db.Text, db.ForeignKey('pais.pais'), primary_key=True)
    indicador = db.Column(db.Text, primary_key=True)
    fecha = db.Column(db.Date, primary_key=True)
    # FORZAMOS todos a Text para evitar conversión
    coal_peat_oil_shale  = db.Column(db.Text)
    natural_gas          = db.Column(db.Text)
    nuclear              = db.Column(db.Text)
    oil_products         = db.Column(db.Text)
    renewables_and_waste = db.Column(db.Text)
    total                = db.Column(db.Text)

class HistoricoConsumoProduccion(db.Model):
    __tablename__ = 'historico_consumo_produccion'  
    __table_args__ = {'extend_existing': True}  # CLAVE: Fuerza a redefinir la tabla
    
    pais = db.Column(db.Text, db.ForeignKey('pais.pais'), primary_key=True)
    indicador = db.Column(db.Text, primary_key=True)
    anio = db.Column(db.Integer, primary_key=True)
    # FORZAMOS todos a Text para evitar conversión
    coal_peat_oil_shale  = db.Column(db.Text)
    natural_gas          = db.Column(db.Text)
    nuclear              = db.Column(db.Text)
    oil_products         = db.Column(db.Text)
    renewables_and_waste = db.Column(db.Text)
    total                = db.Column(db.Text)

def safe_float(value):
    """Convierte un valor a float de forma segura"""
    if value is None or value == '' or value == 'NULL':
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

# --- Rutas ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug')
def debug_db():
    """Verificar que ahora sí conecta a la BD correcta"""
    try:
        paises_count = Pais.query.count()
        actual_count = ActualConsumoProduccion.query.count()
        historico_count = HistoricoConsumoProduccion.query.count()
        
        paises_list = [p.pais for p in Pais.query.limit(10).all()]
        
        # Vamos a ver algunos datos problemáticos
        sample_pais = Pais.query.first()
        sample_actual = ActualConsumoProduccion.query.first()
        
        result = f"""
        <h1>Verificación de BD: backend/bd/energy.db</h1>
        <ul>
            <li><strong>Países:</strong> {paises_count} registros</li>
            <li><strong>Consumos Actuales:</strong> {actual_count} registros</li>
            <li><strong>Históricos:</strong> {historico_count} registros</li>
        </ul>
        
        <h2>Primeros 10 países encontrados:</h2>
        <ul>
        """
        
        for pais in paises_list:
            result += f"<li>{pais}</li>"
        
        result += "</ul>"
        
        if sample_pais:
            result += f"""
            <h2>Datos de muestra - País:</h2>
            <ul>
                <li>País: {sample_pais.pais}</li>
                <li>PIB Anual: {sample_pais.pib_anual}</li>
                <li>PIB Per Capita: {sample_pais.pib_per_capita}</li>
                <li>CO2 Per Capita: {sample_pais.co2_per_capita}</li>
            </ul>
            """
        
        if sample_actual:
            result += f"""
            <h2>Datos de muestra - Consumo Actual:</h2>
            <ul>
                <li>País: {sample_actual.pais}</li>
                <li>Indicador: {sample_actual.indicador}</li>
                <li>Fecha: {sample_actual.fecha}</li>
                <li>Coal: {sample_actual.coal_peat_oil_shale}</li>
                <li>Gas: {sample_actual.natural_gas}</li>
                <li>Total: {sample_actual.total}</li>
            </ul>
            """
        
        return result
    except Exception as e:
        return f"<h1>Error al conectar con la BD:</h1><p>{str(e)}</p><pre>{repr(e)}</pre>"

@app.route('/consumo', methods=['GET','POST'])
def show_consumption():
    # — 1) cargar siempre las listas para los desplegables y tablas
    try:
        paises = [p.pais for p in Pais.query.order_by(Pais.pais).all()]
        indicadores = [i[0] for i in db.session.query(
                           ActualConsumoProduccion.indicador
                       ).distinct().order_by(ActualConsumoProduccion.indicador).all()]
        anios = [y[0] for y in db.session.query(
                     HistoricoConsumoProduccion.anio
                 ).distinct().order_by(HistoricoConsumoProduccion.anio).all()]
        actual_list = ActualConsumoProduccion.query.order_by(
                          ActualConsumoProduccion.pais,
                          ActualConsumoProduccion.indicador,
                          ActualConsumoProduccion.fecha
                      ).all()
        historico_list = HistoricoConsumoProduccion.query.order_by(
                             HistoricoConsumoProduccion.pais,
                             HistoricoConsumoProduccion.indicador,
                             HistoricoConsumoProduccion.anio
                         ).all()
    except Exception as e:
        # Si hay error, devolvemos listas vacías y mostramos el error
        return f"<h1>Error cargando datos:</h1><p>{str(e)}</p><pre>{repr(e)}</pre>"

    datos = None
    if request.method == 'POST':
        # — 2) usar .get para no lanzar KeyError
        pais_sel = request.form.get('pais')
        ind_sel  = request.form.get('indicador')
        anio_sel = request.form.get('anio', type=int)

        if pais_sel and ind_sel:
            try:
                actual = ActualConsumoProduccion.query\
                    .filter_by(pais=pais_sel, indicador=ind_sel)\
                    .order_by(ActualConsumoProduccion.fecha.desc())\
                    .first()

                if actual:
                    year = actual.fecha.year
                    target_year = anio_sel or year
                    historico = HistoricoConsumoProduccion.query.filter_by(
                        pais=pais_sel,
                        indicador=ind_sel,
                        anio=target_year
                    ).first()

                    datos = {
                        'pais': pais_sel,
                        'indicador': ind_sel,
                        'fecha_actual': actual.fecha,
                        'valores_actual': {
                            'coal': safe_float(actual.coal_peat_oil_shale),
                            'gas': safe_float(actual.natural_gas),
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
                            'gas': safe_float(historico.natural_gas),
                            'nuclear': safe_float(historico.nuclear),
                            'oil': safe_float(historico.oil_products),
                            'renwaste': safe_float(historico.renewables_and_waste),
                            'total': safe_float(historico.total),
                        }
            except Exception as e:
                # Si hay error en la consulta específica, mostramos el error
                datos = {'error': f'Error procesando consulta: {str(e)}'}

    return render_template(
        'consumo_comparador.html',
        paises=paises,
        indicadores=indicadores,
        anios=anios,
        actual_list=actual_list,
        historico_list=historico_list,
        datos=datos
    )

if __name__ == "__main__":
    # Crea las tablas si no existen (pero ahora en la BD correcta)
    with app.app_context():
        db.create_all()
    app.run(debug=True)