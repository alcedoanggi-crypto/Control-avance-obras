# 🚧 Control de Avance de Obra

Sistema web para la supervisión y seguimiento del avance físico y financiero
de obras de construcción, organizado por proyecto, disciplina y partida.
Construido con **Flask** (patrón MVC) y **PostgreSQL**.

## Índice

- [Características](#características)
- [Capturas de pantalla](#capturas-de-pantalla)
- [Stack tecnológico](#stack-tecnológico)
- [Instalación](#instalación)
- [Estructura del proyecto](#estructura-del-proyecto)

## Características

- 📁 Gestión de proyectos (obras), disciplinas y partidas.
- 🗓️ Cronograma visual por disciplina, con avance por fecha de corte.
- ✅ Registro de avance de partidas con evidencia fotográfica.
- 📊 Dashboard en tiempo real: presupuesto vs. ejecutado, curva S,
  distribución por disciplina y partidas críticas.
- 📄 Reportes exportables en PDF y Excel.
- 👥 Control de acceso por roles: administrador, supervisor/residente y
  cliente/visualizador.

## Capturas de pantalla

| Login | Dashboard |
|---|---|
| ![Login](docs/screenshots/login.png) | ![Dashboard](docs/screenshots/dashboard.png) |

| Cronograma | Actualizar avance |
|---|---|
| ![Cronograma](docs/screenshots/cronograma.png) | ![Actualizar avance](docs/screenshots/actualizar_avance.png) |

| Proyectos | Reportes |
|---|---|
| ![Proyectos](docs/screenshots/proyectos.png) | ![Reportes](docs/screenshots/reportes.png) |

## Stack tecnológico

- **Backend:** Flask 3, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF
- **Base de datos:** PostgreSQL
- **Reportes:** ReportLab (PDF), OpenPyXL (Excel)
- **Frontend:** Jinja2, Bootstrap 5, Chart.js

## Instalación

### Requisitos previos

- Python 3.11+
- PostgreSQL 14+

### Pasos

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/alcedoanggi-crypto/Control-avance-obras.git
   cd Control-avance-obras
   ```

2. Crear y activar un entorno virtual, luego instalar dependencias:

   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   # source venv/bin/activate     # Linux / macOS
   pip install -r requirements.txt
   ```

3. Crear la base de datos y el rol de aplicación (ver `scripts/crear_bd.sql`):

   ```bash
   psql -U postgres -f scripts/crear_bd.sql
   ```

4. Crear un archivo `.env` en la raíz del proyecto:

   ```env
   SECRET_KEY=cambia-esta-clave
   DATABASE_URL=postgresql+psycopg2://avance_app:avance_pass@localhost:5432/control_avance_obra
   DIAS_ALERTA_SIN_ACTUALIZAR=15
   FLASK_APP=run.py
   FLASK_DEBUG=1
   PORT=5058
   ```

5. Aplicar las migraciones:

   ```bash
   flask db upgrade
   ```

6. Ejecutar la aplicación:

   ```bash
   python run.py
   ```

   La aplicación quedará disponible en `http://127.0.0.1:5058`.

## Estructura del proyecto

```
app/
├── controllers/   # Blueprints / rutas (auth, proyectos, avance, reportes, ...)
├── models/        # Modelos SQLAlchemy
├── services/       # Lógica de negocio
├── static/        # CSS, JS y archivos subidos
├── templates/     # Vistas Jinja2
├── config.py
├── extensions.py
└── forms.py
scripts/           # Scripts SQL de utilidad
run.py             # Punto de entrada
```
