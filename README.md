# BackIsi

## Autores

- **Alfonso Julián Zapata Velasco**  
- **Álvaro González Luque**  
- **Juan Barea Rojo**

---

## 1. Proyecto: Comparativa de la Viabilidad Energética de Data Centers

Estudio sobre la **viabilidad energética de los data centers** en España en comparación con otras regiones del mundo.  
Se analizarán factores como:

- Disponibilidad y coste de la energía
- Infraestructura y capacidad eléctrica
- Políticas y regulaciones
- Competitividad y atracción de inversión

**Objetivo Principal**: Evaluar si España puede competir globalmente como ubicación para grandes infraestructuras digitales.

---

## 2. Estructura del proyecto

Este proyecto se organiza de la siguiente manera:

```plaintext
mi_proyecto/
│
├── app/                 # Contiene el código principal de la aplicación Flask
│   ├── templates/       # Archivos HTML para las vistas
│   │   ├── add_project.html  # Formulario para agregar un proyecto
│   │   └── index.html      # Página principal con la lista de proyectos
│   └── app.py           # Archivo principal de la aplicación Flask
│
├── BBDD/                # Carpeta que contiene los scripts relacionados con la base de datos
│   ├──scrapping/        # Carpeta dedicada a la obtención de datos para el sistema (scrapping, api...)
│   │  ├── api_mix.py    # Acceso a los datos de la API [electricity maps](https://portal.electricitymaps.com/)
│   │
│   ├── createBBDD.py    # Script para crear la base de datos y las tablas necesarias
│   ├── modifyBBDD.py    # Script para modificar o agregar datos a la base de datos
│   └── readBBDD.py      # Script para leer los datos de la base de datos
│
├── .gitignore           # Archivos y carpetas que deben ser ignorados por git
├── LICENSE              # Licencia del proyecto
├── README.md            # Documentación del proyecto
├── requirements.txt     # Dependencias necesarias para ejecutar el proyecto
└── bd_energy.db         # Archivo de base de datos SQLite donde se almacenan los proyectos de energía
```

---

### ¿Cómo Ejecutar el Proyecto?

1. Clona el repositorio:

   ```bash
   git clone <URL-del-repositorio>
   ```

2. Instala las dependencias necesarias:

   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la aplicación Flask:

   ```bash
   python app/app.py
   ```

4. Accede a la aplicación en tu navegador en la dirección [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

### Notas de desarrollo

- [Uso de dependencias](https://github.com/AlfonsoJulian/BackIsi/pull/20#issuecomment-2704798823)