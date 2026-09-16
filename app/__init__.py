"""Fabrica de la aplicacion (patron Application Factory)."""
import os
from flask import Flask, render_template

from app.config import Config
from app.extensions import db, migrate, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models.usuario import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    # Blueprints (controladores)
    from app.controllers.auth import auth_bp
    from app.controllers.dashboard import dashboard_bp
    from app.controllers.proyectos import proyectos_bp
    from app.controllers.partidas import partidas_bp
    from app.controllers.avance import avance_bp
    from app.controllers.reportes import reportes_bp
    from app.controllers.usuarios import usuarios_bp
    from app.controllers.cronograma import cronograma_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(proyectos_bp)
    app.register_blueprint(partidas_bp)
    app.register_blueprint(avance_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(cronograma_bp)

    # CLI
    from app.cli import register_cli
    register_cli(app)

    # Contexto de plantillas: proyecto activo / lista de proyectos accesibles
    from app.utils import proyecto_actual, proyectos_accesibles

    @app.context_processor
    def inject_proyecto():
        return {"proyecto_actual": proyecto_actual(), "proyectos_accesibles": proyectos_accesibles()}

    # Errores
    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("errors.html", codigo=403,
                               mensaje="No tienes permiso para ver esta pagina."), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors.html", codigo=404,
                               mensaje="La pagina solicitada no existe."), 404

    # Filtros de plantilla
    @app.template_filter("moneda")
    def moneda(valor):
        try:
            return f"$ {float(valor):,.2f}"
        except (TypeError, ValueError):
            return "$ 0.00"

    @app.template_filter("porcentaje")
    def porcentaje(valor):
        try:
            return f"{float(valor) * 100:.1f}%"
        except (TypeError, ValueError):
            return "0.0%"

    return app
