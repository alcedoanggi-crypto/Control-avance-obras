"""Modelo Usuario y roles del sistema."""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.proyecto import usuarios_proyectos


class RolUsuario:
    ADMIN = "administrador"
    SUPERVISOR = "supervisor"
    CLIENTE = "cliente"

    OPCIONES = (ADMIN, SUPERVISOR, CLIENTE)
    ETIQUETAS = {
        ADMIN: "Administrador",
        SUPERVISOR: "Residente / Supervisor de obra",
        CLIENTE: "Cliente / Visualizador",
    }


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default=RolUsuario.CLIENTE)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    proyectos = db.relationship(
        "Proyecto", secondary=usuarios_proyectos, back_populates="usuarios",
    )
    actualizaciones = db.relationship("HistorialAvance", back_populates="usuario")

    # -- password ----------------------------------------------------------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # -- helpers -------------------------------------------------------------
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def es_admin(self):
        return self.rol == RolUsuario.ADMIN

    @property
    def es_supervisor(self):
        return self.rol == RolUsuario.SUPERVISOR

    @property
    def es_cliente(self):
        return self.rol == RolUsuario.CLIENTE

    @property
    def rol_etiqueta(self):
        return RolUsuario.ETIQUETAS.get(self.rol, self.rol)

    def tiene_acceso(self, proyecto):
        return self.es_admin or proyecto in self.proyectos

    def __repr__(self):
        return f"<Usuario {self.email} ({self.rol})>"
