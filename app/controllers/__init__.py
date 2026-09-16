"""Utilidades compartidas por los controladores (blueprints): control de acceso por rol."""
from functools import wraps

from flask import abort
from flask_login import current_user

from app.models.usuario import RolUsuario


def role_required(*roles):
    """Permite el acceso solo a los roles indicados.

    Uso: @role_required(RolUsuario.ADMIN, RolUsuario.SUPERVISOR)
    """

    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.rol not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapper

    return decorator


admin_required = role_required(RolUsuario.ADMIN)
gestion_avance_required = role_required(RolUsuario.ADMIN, RolUsuario.SUPERVISOR)
