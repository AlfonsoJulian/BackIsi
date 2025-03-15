### 📄 **README.md**
# BackIsi

## Autores

- **Alfonso Julián Zapata Velasco**  
- **Álvaro González Luque**  
- **Juan Barea Rojo**

---

## 1️⃣ Proyecto: Comparativa de la Viabilidad Energética de Data Centers

Este proyecto estudia la **viabilidad energética de los data centers** en España en comparación con otras regiones del mundo.  
Se analizan factores clave como:

- Disponibilidad y coste de la energía  
- Infraestructura y capacidad eléctrica  
- Políticas y regulaciones  
- Competitividad y atracción de inversión  

### 🎯 **Objetivo Principal**
Evaluar si España puede competir globalmente como ubicación para grandes infraestructuras digitales.

---

## 2️⃣ Estructura del Proyecto

Este proyecto está estructurado de la siguiente manera:

```plaintext
BackIsi/
│
├── app/                 # Aplicación Flask
│   ├── templates/       # Archivos HTML para las vistas
│   │   ├── index.html              # Página principal con opciones
│   │   ├── show_consumption.html    # Tabla de consumo de energía
│   │   ├── show_production.html     # Tabla de producción de energía
│   ├── static/          # Archivos estáticos como CSS y JS
│   ├── routes.py        # Define las rutas de la aplicación Flask
│   ├── main.py          # Archivo principal para ejecutar la app Flask
│   ├── __init__.py      # Inicialización del módulo
│
├── backend/             # Lógica de negocio y acceso a la base de datos
│   ├── database.py      # Gestión de la base de datos SQLite
│   ├── energy_service.py # Servicio para obtener y procesar datos
│   ├── models.py        # Definición de las clases de datos
│   ├── __init__.py      # Inicialización del módulo
│
├── scrapping/           # Módulo para obtener datos desde API y web scraping
│   ├── api_client.py    # Cliente API para obtener datos de energía
│   ├── scraping_prices.py # Web Scraping de precios de electricidad
│   ├── __init__.py      # Inicialización del módulo
│
├── data/                # Contiene archivos de datos
│   ├── bd_energy.db     # Base de datos SQLite
│   ├── electricity_prices.csv # Datos de precios de electricidad extraídos
│
├── tests/               # Pruebas unitarias para el proyecto
│   ├── test_api_client.py      # Pruebas para API de electricidad
│   ├── test_database.py        # Pruebas para base de datos
│   ├── test_energy_service.py  # Pruebas para servicios de energía
│
├── LICENSE              # Licencia del proyecto
├── README.md            # Documentación del proyecto
├── requirements.txt     # Dependencias necesarias para ejecutar el proyecto
└── .gitignore           # Archivos y carpetas que deben ser ignorados por git
```

---

## 3️⃣ 🚀 **Cómo Ejecutar el Proyecto**

1. **Clona el repositorio**:

   ```bash
   git clone <URL-del-repositorio>
   cd BackIsi
   ```

2. **Instala las dependencias necesarias**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecuta la aplicación Flask**:

   ```bash
   python -m app.main
   ```

4. **Accede a la aplicación en tu navegador**:

   [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 4️⃣ 📌 **Uso de la Aplicación**

### **✔️ Rutas Disponibles**
| Ruta                | Método | Descripción |
|---------------------|--------|-------------|
| `/`                | `GET`  | Página principal |
| `/show_consumption` | `GET`  | Muestra la tabla de consumo energético |
| `/show_production`  | `GET`  | Muestra la tabla de producción energética |
| `/update_data`      | `POST` | Obtiene datos actualizados desde la API |
| `/update_prices`    | `POST` | Ejecuta el scraping y actualiza precios |

### **✔️ API de Datos de Energía**
Este proyecto usa datos de **[Electricity Maps](https://portal.electricitymaps.com/)** para obtener información sobre la mezcla de generación de energía por país.

### **✔️ Scraping de Precios**
Los datos de precios de electricidad se extraen de **[DatosMacro](https://datosmacro.expansion.com/)** mediante técnicas de Web Scraping.

---

## 5️⃣ 📌 **Notas de Desarrollo**

- **Manejo de dependencias**: [Repositorio en GitHub](https://github.com/AlfonsoJulian/BackIsi/pull/20#issuecomment-2704798823)  
- **Pruebas unitarias en `tests/`**  
- **Implementación modular usando Flask y POO**  

---

## 6️⃣ 📜 **Licencia**
Este proyecto está licenciado bajo **MIT License**. Ver [LICENSE](./LICENSE) para más detalles.