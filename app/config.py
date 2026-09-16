"""Configuracion de la aplicacion."""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-no-usar-en-produccion")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://avance_app:avance_pass@localhost:5432/control_avance_obra",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Reglas de negocio
    DIAS_ALERTA_SIN_ACTUALIZAR = int(os.getenv("DIAS_ALERTA_SIN_ACTUALIZAR", 15))

    # Subida de evidencias fotograficas
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads", "evidencias")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
