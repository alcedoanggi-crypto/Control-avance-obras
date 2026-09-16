"""Helpers de proyecto activo (soporte multi-obra via sesion)."""
from flask import session
from flask_login import current_user

from app.models.proyecto import Proyecto


def proyectos_accesibles():
    if not current_user.is_authenticated:
        return []
    if current_user.es_admin:
        return Proyecto.query.filter_by(activo=True).order_by(Proyecto.nombre).all()
    return sorted((p for p in current_user.proyectos if p.activo), key=lambda p: p.nombre)


def proyecto_actual():
    proyectos = proyectos_accesibles()
    if not proyectos:
        return None
    proyecto_id = session.get("proyecto_id")
    if proyecto_id:
        for p in proyectos:
            if p.id == proyecto_id:
                return p
    return proyectos[0]
