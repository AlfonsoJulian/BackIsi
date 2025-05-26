# Importación de Flask y componentes necesarios para crear la aplicación web
from flask import Flask, render_template, request, jsonify
# Importación de SQLAlchemy para manejo de base de datos
from flask_sqlalchemy import SQLAlchemy
# Importación de módulos para manejo de fechas y números decimales
from datetime import datetime, date
from decimal import Decimal
# Importación de módulos del sistema operativo, expresiones regulares y ejecución de scripts
import os, re, runpy
# Importación adicional de Flask para manejo de errores HTTP
from flask import abort

# Creación de la instancia de la aplicación Flask
app = Flask(__name__)
# Obtención del directorio base donde se encuentra el archivo actual
basedir = os.path.abspath(os.path.dirname(__file__))
# Construcción de la ruta hacia la base de datos SQLite
db_path = os.path.join(basedir, 'backend', 'bd', 'energy.db')
# Configuración de la URI de la base de datos para SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
# Desactivación del seguimiento de modificaciones para mejorar rendimiento
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Inicialización del objeto SQLAlchemy con la aplicación Flask
db = SQLAlchemy(app)

# Constante para convertir de MegaWatt-hora a PetaJoules
MWH_TO_PJ    = 3.6e-6
# Constante para convertir horas a año (24 horas * 365 días)
HOUR_TO_YEAR = 24 * 365

# --- UTILIDADES ---
# Función para convertir valores a float de manera segura
def safe_float(value):
    # Si el valor es None, cadena vacía o 'NULL', retorna 0.0
    if value in (None, '', 'NULL'):
        return 0.0
    # Intenta convertir a float, si falla retorna 0.0
    try:
        return float(value)
    except:
        return 0.0

# Función para parsear fechas de manera segura desde strings
def parse_date_safe(date_str):
    # Si no hay cadena de fecha, retorna None
    if not date_str:
        return None
    # Si la fecha termina en 'Z' (UTC), la elimina
    if isinstance(date_str, str) and date_str.endswith('Z'):
        date_str = date_str[:-1]
    # Lista de formatos de fecha a probar
    for fmt in ('%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d'):
        try:
            # Intenta parsear la fecha con cada formato y retorna solo la fecha (sin hora)
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            # Si falla, continúa con el siguiente formato
            continue
    # Si ningún formato funciona, retorna None
    return None

# Función para extraer el año de un objeto fecha
def get_year_from_date(date_value):
    # Si el objeto tiene atributo 'year', lo retorna
    if hasattr(date_value, 'year'):
        return date_value.year
    # Si no, retorna None
    return None

# Función para convertir strings a formato camelCase
def to_camel_case(s: str) -> str:
    # Encuentra todas las palabras alfanuméricas
    parts = re.findall(r'[A-Za-z0-9]+', s)
    # Convierte todas las partes a minúsculas
    parts = [p.lower() for p in parts]
    # Retorna la primera parte en minúsculas y las demás con primera letra mayúscula
    return parts[0] + ''.join(p.title() for p in parts[1:]) if parts else ''

# --- MODELOS ---
# Modelo de base de datos para la tabla 'pais'
class Pais(db.Model):
    # Nombre de la tabla en la base de datos
    __tablename__ = 'pais'
    # Permite extender la tabla si ya existe
    __table_args__ = {'extend_existing': True}

    # Columna primary key que almacena el nombre del país
    pais             = db.Column(db.Text, primary_key=True)
    # Columna para almacenar el PIB anual del país
    pib_anual        = db.Column(db.Text)
    # Columna para almacenar el PIB per cápita
    pib_per_capita   = db.Column(db.Text)
    # Columna para almacenar las emisiones de CO2 per cápita
    co2_per_capita   = db.Column(db.Text)

    # Relación uno a muchos con la tabla de consumo/producción actual
    consumos         = db.relationship('ActualConsumoProduccion', backref='pais_obj')
    # Relación uno a muchos con la tabla de consumo/producción histórico
    historicos       = db.relationship('HistoricoConsumoProduccion', backref='pais_obj')
    # Relación uno a muchos con la tabla de precios históricos
    precios_historico = db.relationship('HistoricoPrecio', backref='pais_obj')

    # Atributos de simulador (no persistidos en base de datos)
    # Contador de datacenters comprados
    _datacenters_owned = 0
    # Contador de plantas de energía compradas
    _powerplants_owned = 0

    # Método para comprar datacenters usando precio histórico sin impuesto
    def buy_datacenters(self, count: int, year: int, capacity_kw: Decimal) -> Decimal:
        """Compra datacenters usando precio histórico sin impuesto."""
        # Busca el registro de precio histórico para el año especificado
        record = next((hp for hp in self.precios_historico if hp.anio == year), None)
        # Si no encuentra precio para ese año, lanza excepción
        if not record:
            raise ValueError(f'No hay precio histórico para {self.pais} en {year}')
        # Calcula el costo total: precio por kW * capacidad * cantidad
        cost = record.precio_kw * capacity_kw * count
        # Incrementa el contador de datacenters
        self._datacenters_owned += count
        # Retorna el costo calculado
        return cost

    # Método para comprar plantas de energía usando precio con impuesto
    def buy_powerplants(self, count: int, year: int, capacity_kw: Decimal) -> Decimal:
        """Compra centrales usando precio con impuesto."""
        # Busca el registro de precio histórico para el año especificado
        record = next((hp for hp in self.precios_historico if hp.anio == year), None)
        # Si no encuentra precio para ese año, lanza excepción
        if not record:
            raise ValueError(f'No hay precio histórico para {self.pais} en {year}')
        # Calcula el costo total usando precio con impuesto
        cost = record.precio_kw_impuesto * capacity_kw * count
        # Incrementa el contador de plantas de energía
        self._powerplants_owned += count
        # Retorna el costo calculado
        return cost

    # Método para simular el impacto energético de las compras
    def simulate_energy_impact(self) -> dict:
        """Calcula consumo y producción anual en MWh y PJ."""
        # Calcula consumo anual de datacenters (kW→kWh→MWh)
        annual_dc_mwh = (self._datacenters_owned *
                         getattr(self, '_dc_capacity_kw', 0) *
                         HOUR_TO_YEAR) / 1000
        # Calcula producción anual de plantas (kW→kWh→MWh)
        annual_pp_mwh = (self._powerplants_owned *
                         getattr(self, '_pp_capacity_kw', 0) *
                         HOUR_TO_YEAR) / 1000
        # Calcula el balance neto (producción - consumo)
        net_mwh = annual_pp_mwh - annual_dc_mwh
        # Retorna diccionario con todos los valores calculados
        return {
            'datacenters_mwh': annual_dc_mwh,
            'powerplants_mwh': annual_pp_mwh,
            'net_mwh': net_mwh,
            'net_pj': net_mwh * MWH_TO_PJ
        }

    # Método para registrar resultados de simulación en la base de datos
    def record_simulation(self, indicador: str) -> 'ActualConsumoProduccion':
        """Guarda resultado neto en actual_consumo_produccion."""
        # Obtiene el impacto energético calculado
        impact = self.simulate_energy_impact()
        # Obtiene la fecha actual
        today = date.today()
        # Convierte el valor neto a Decimal para precisión
        total = Decimal(str(impact['net_mwh']))
        # Busca si ya existe un registro para este país, indicador y fecha
        actual = ActualConsumoProduccion.query.get((self.pais, indicador, today.isoformat()))
        # Si no existe, crea un nuevo registro
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
            # Añade el nuevo registro a la sesión
            db.session.add(actual)
        else:
            # Si existe, actualiza solo el total
            actual.total = str(total)
        # Confirma los cambios en la base de datos
        db.session.commit()
        # Retorna el registro actualizado
        return actual


# Modelo para la tabla de consumo/producción actual
class ActualConsumoProduccion(db.Model):
    # Nombre de la tabla en la base de datos
    __tablename__ = 'actual_consumo_produccion'
    # Permite extender la tabla si ya existe
    __table_args__ = {'extend_existing': True}

    # Clave primaria compuesta: país (con foreign key)
    pais                 = db.Column(db.Text, db.ForeignKey('pais.pais'), primary_key=True)
    # Clave primaria compuesta: indicador
    indicador            = db.Column(db.Text, primary_key=True)
    # Clave primaria compuesta: fecha
    fecha                = db.Column(db.Text, primary_key=True)
    # Columnas para diferentes tipos de combustibles/energías
    coal_peat_oil_shale  = db.Column(db.Text)  # Carbón, turba, esquisto bituminoso
    natural_gas          = db.Column(db.Text)  # Gas natural
    nuclear              = db.Column(db.Text)  # Energía nuclear
    oil_products         = db.Column(db.Text)  # Productos petrolíferos
    renewables_and_waste = db.Column(db.Text)  # Renovables y residuos
    total                = db.Column(db.Text)  # Total


# Modelo para la tabla de consumo/producción histórico
class HistoricoConsumoProduccion(db.Model):
    # Nombre de la tabla en la base de datos
    __tablename__ = 'historico_consumo_produccion'
    # Permite extender la tabla si ya existe
    __table_args__ = {'extend_existing': True}

    # Clave primaria compuesta: país (con foreign key)
    pais                 = db.Column(db.Text, db.ForeignKey('pais.pais'), primary_key=True)
    # Clave primaria compuesta: indicador
    indicador            = db.Column(db.Text, primary_key=True)
    # Clave primaria compuesta: año
    anio                 = db.Column(db.Integer, primary_key=True)
    # Columnas para diferentes tipos de combustibles/energías (igual que la tabla actual)
    coal_peat_oil_shale  = db.Column(db.Text)
    natural_gas          = db.Column(db.Text)
    nuclear              = db.Column(db.Text)
    oil_products         = db.Column(db.Text)
    renewables_and_waste = db.Column(db.Text)
    total                = db.Column(db.Text)


# Modelo para la tabla de precios históricos
class HistoricoPrecio(db.Model):
    # Nombre de la tabla en la base de datos
    __tablename__ = 'historico_precio'
    # Permite extender la tabla si ya existe
    __table_args__ = {'extend_existing': True}

    # Clave primaria compuesta: país (con foreign key)
    pais               = db.Column(db.Text, db.ForeignKey('pais.pais'), primary_key=True)
    # Clave primaria compuesta: año
    anio               = db.Column(db.Integer, primary_key=True)
    # Precio por kW con impuesto (20 dígitos, 8 decimales)
    precio_kw_impuesto = db.Column(db.Numeric(20, 8))
    # Precio por kW sin impuesto
    precio_kw          = db.Column(db.Numeric(20, 8))
    # Comentario: aquí NO se define otro relationship; se hereda de Pais.precios_historico

# --- RUTAS PRINCIPALES ---
# Ruta para la página principal
@app.route('/')
def index():
    # Renderiza la plantilla HTML de la página principal
    return render_template('index.html')

# Ruta para mostrar consumo (acepta GET y POST)
@app.route('/consumo', methods=['GET','POST'])
def show_consumption():
    try:
        # Obtiene lista de todos los países ordenados alfabéticamente
        paises = [p.pais for p in Pais.query.order_by(Pais.pais)]
        # Obtiene lista de indicadores únicos ordenados
        indicadores = [i[0] for i in db.session.query(
                           ActualConsumoProduccion.indicador
                       ).distinct().order_by(ActualConsumoProduccion.indicador).all()]
        # Obtiene lista de años únicos ordenados
        anios = [y[0] for y in db.session.query(
                     HistoricoConsumoProduccion.anio
                 ).distinct().order_by(HistoricoConsumoProduccion.anio).all()]

        # Desactiva el autoflush para evitar commits automáticos
        with db.session.no_autoflush:
            # Obtiene todos los registros actuales ordenados
            actual_list = ActualConsumoProduccion.query.order_by(
                              ActualConsumoProduccion.pais,
                              ActualConsumoProduccion.indicador,
                              ActualConsumoProduccion.fecha
                          ).all()
            # Para cada registro, parsea la fecha de manera segura
            for a in actual_list:
                a.fecha_parsed = parse_date_safe(a.fecha)

        # Obtiene todos los registros históricos ordenados
        historico_list = HistoricoConsumoProduccion.query.order_by(
                             HistoricoConsumoProduccion.pais,
                             HistoricoConsumoProduccion.indicador,
                             HistoricoConsumoProduccion.anio
                         ).all()
    except Exception as e:
        # Si hay error, retorna página de error
        return f"<h1>Error cargando datos:</h1><p>{e}</p>"

    # Inicializa datos como None
    datos = None
    # Si es una petición POST (formulario enviado)
    if request.method == 'POST':
        # Obtiene los valores del formulario
        pais_sel = request.form.get('pais')
        ind_sel  = request.form.get('indicador')
        anio_sel = request.form.get('anio', type=int)
        # Si se seleccionaron país e indicador
        if pais_sel and ind_sel:
            try:
                # Busca el registro actual más reciente
                actual = (ActualConsumoProduccion.query
                          .filter_by(pais=pais_sel, indicador=ind_sel)
                          .order_by(ActualConsumoProduccion.fecha.desc())
                          .first())
                # Si encuentra registro actual
                if actual:
                    # Parsea la fecha del registro actual
                    fecha_parseada = parse_date_safe(actual.fecha) or actual.fecha
                    # Extrae el año de la fecha parseada
                    year = get_year_from_date(fecha_parseada) or get_year_from_date(actual.fecha)
                    # Usa el año seleccionado o el año del registro
                    target_year = anio_sel or year

                    # Busca el registro histórico correspondiente
                    historico = HistoricoConsumoProduccion.query.filter_by(
                        pais=pais_sel,
                        indicador=ind_sel,
                        anio=target_year
                    ).first()

                    # Prepara los datos para mostrar
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
                    # Si encuentra registro histórico, añade sus valores
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
                # Si hay error, guarda el mensaje de error
                datos = {'error': str(e)}

    # Renderiza la plantilla con todos los datos
    return render_template(
        'consumo_comparador.html',
        paises=paises,
        indicadores=indicadores,
        anios=anios,
        actual_list=actual_list,
        historico_list=historico_list,
        datos=datos
    )

# Ruta para el simulador
@app.route('/simulador')
def simulador():
    # Obtiene lista de países ordenados
    paises = [p.pais for p in Pais.query.order_by(Pais.pais)]
    # Renderiza la plantilla del simulador
    return render_template('simulador.html', paises=paises)

# --- RUTA PARA ACTUALIZAR DATOS ---
# Ruta para actualizar datos de consumo ejecutando script externo
@app.route('/update_consumo')
def update_consumo():
    # Ruta del script Python para actualizar datos
    script_path = r'C:\Users\Usuario\Desktop\facultad\cuarto\2CUATRI\isi\practicas\BackIsi\backend\scrapping\api_mix.py'
    try:
        # Ejecuta el script externo
        runpy.run_path(script_path, run_name="__main__")
    except Exception as e:
        # Si hay error, retorna mensaje de error con código 500
        return f"<h3>Error al actualizar:</h3><pre>{e}</pre>", 500
    # Si todo va bien, retorna mensaje de éxito
    return "<h3>Datos actualizados correctamente llamando a api_mix.py.</h3>"


# API endpoint para simulación (acepta solo POST)
@app.route('/api/simulate', methods=['POST'])
def simulate_route():
    # Obtiene los datos JSON de la petición
    p = request.get_json(force=True)
    # Extrae los parámetros del JSON
    pais_key = p.get('pais')                    # País seleccionado
    year     = p.get('year')                    # Año para precios
    dc       = int(p.get('datacenters',  0))    # Número de datacenters
    dc_kw    = Decimal(str(p.get('dc_capacity_kw', 0)))  # Capacidad DC en kW
    pp       = int(p.get('powerplants',  0))    # Número de plantas
    pp_kw    = Decimal(str(p.get('pp_capacity_kw', 0)))  # Capacidad PP en kW
    record   = p.get('record', False)           # Si guardar en BD
    indicator= p.get('indicator', 'simulacion') # Indicador a usar

    # 1) Busca el país en la base de datos o retorna error 404
    pais   = db.session.get(Pais, pais_key) or abort(404, f'País "{pais_key}" no existe')
    # Busca el precio histórico para el año especificado o retorna error 400
    precio = (HistoricoPrecio
              .query
              .filter_by(pais=pais_key, anio=year)
              .first()) or abort(400, f'No hay precio para {year}')

    # 2) Calcula los costos de datacenters y plantas
    cost_dc = precio.precio_kw          * dc_kw * dc  # Costo DC (sin impuesto)
    cost_pp = precio.precio_kw_impuesto * pp_kw * pp  # Costo PP (con impuesto)

    # 3) Calcula el impacto energético anual
    # Consumo de datacenters: kW * cantidad * horas/año / 1000 (para MWh)
    cons_mwh = dc_kw * dc * HOUR_TO_YEAR / Decimal(1000)
    # Producción de plantas: kW * cantidad * horas/año / 1000 (para MWh)
    prod_mwh = pp_kw * pp * HOUR_TO_YEAR / Decimal(1000)
    # Balance neto: producción - consumo
    net_mwh  = prod_mwh - cons_mwh
    # Conversión a PetaJoules
    net_pj   = net_mwh * Decimal(str(MWH_TO_PJ))

    # Prepara el resultado para retornar
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

    # 4) Si se solicita grabar en base de datos
    if record:
        # Crea nuevo registro en la tabla actual
        act = ActualConsumoProduccion(
            pais=pais_key,
            indicador=indicator,
            fecha=date.today().isoformat(),  # Fecha actual
            coal_peat_oil_shale='0',        # Todos en cero excepto total
            natural_gas='0',
            nuclear='0',
            oil_products='0',
            renewables_and_waste='0',
            total=str(net_mwh)              # Solo el total neto
        )
        # Añade el registro a la sesión
        db.session.add(act)
        # Confirma los cambios
        db.session.commit()
        # Añade información del registro al resultado
        result['record'] = {
            'fecha':     act.fecha,
            'total_mwh': float(act.total)
        }

    # Retorna el resultado como JSON
    return jsonify(result)

# Punto de entrada principal del programa
if __name__ == "__main__":
    # Crea el contexto de la aplicación
    with app.app_context():
        # Crea todas las tablas en la base de datos
        db.create_all()
    # Ejecuta la aplicación en modo debug
    app.run(debug=True)