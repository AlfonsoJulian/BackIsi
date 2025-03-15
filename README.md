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
.
├── app/          # 📌 Capa de presentación (Frontend y rutas Flask)
│   ├── __init__.py
│   ├── main.py   # 🎯 Punto de entrada de Flask
│   ├── routes.py # 🚏 Define las rutas (endpoints HTTP)
│   ├── static/   # 🎨 Archivos estáticos (CSS, JS, imágenes)
│   ├── templates/ # 🖼 HTML de la aplicación
│
├── backend/      # 📌 Lógica de negocio (procesamiento de datos)
│   ├── database.py # 📊 Manejo de la BD SQLite
│   ├── energy_service.py # ⚡ Procesa datos de consumo/producción energética
│   ├── models.py # 📦 Define estructuras de datos
│
├── data/         # 📌 Almacenamiento local de datos
│   ├── bd_energy.db # 🗄 Base de datos SQLite
│   ├── electricity_prices.csv # 📈 Precios de electricidad scrapados
│
├── scrapping/    # 📌 Obtención de datos externos (APIs y Scraping)
│   ├── api_client.py # 🔗 Conexión con API de energía
│   ├── scraping_prices.py # 🕷 Web scraping de precios eléctricos
│
├── tests/        # 📌 Pruebas automáticas con pytest (python -m pytest tests/) para correrlos
│   ├── test_api_client.py
│   ├── test_database.py
│   ├── test_energy_service.py
│
├── requirements.txt # 📜 Dependencias del proyecto
├── README.md        # 📖 Documentación del proyecto
└── LICENSE          # ⚖ Licencia del proyecto

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