"""Gestion de usuarios y su acceso multi-proyecto. Solo Administrador."""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.controllers import admin_required
from app.extensions import db
from app.models.usuario import Usuario
from app.models.proyecto import Proyecto
from app.forms import UsuarioForm

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def _cargar_opciones_proyecto(form):
    form.proyectos.choices = [(p.id, p.nombre) for p in Proyecto.query.order_by(Proyecto.nombre)]


@usuarios_bp.route("/")
@login_required
@admin_required
def index():
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    return render_template("usuarios/index.html", usuarios=usuarios)


@usuarios_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@admin_required
def nuevo():
    form = UsuarioForm()
    _cargar_opciones_proyecto(form)
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if Usuario.query.filter_by(email=email).first():
            flash("Ya existe un usuario con ese correo.", "warning")
            return render_template("usuarios/form.html", form=form, usuario=None)

        usuario = Usuario(nombre=form.nombre.data.strip(), apellido=form.apellido.data.strip(),
                          email=email, rol=form.rol.data, activo=form.activo.data)
        usuario.set_password(form.password.data or "cambiar123")
        usuario.proyectos = Proyecto.query.filter(Proyecto.id.in_(form.proyectos.data)).all()
        db.session.add(usuario)
        db.session.commit()
        flash("Usuario creado.", "success")
        return redirect(url_for("usuarios.index"))
    return render_template("usuarios/form.html", form=form, usuario=None)


@usuarios_bp.route("/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    form = UsuarioForm(obj=usuario)
    _cargar_opciones_proyecto(form)
    if form.validate_on_submit():
        usuario.nombre = form.nombre.data.strip()
        usuario.apellido = form.apellido.data.strip()
        usuario.email = form.email.data.lower().strip()
        usuario.rol = form.rol.data
        usuario.activo = form.activo.data
        usuario.proyectos = Proyecto.query.filter(Proyecto.id.in_(form.proyectos.data)).all()
        if form.password.data:
            usuario.set_password(form.password.data)
        db.session.commit()
        flash("Usuario actualizado.", "success")
        return redirect(url_for("usuarios.index"))
    if not form.is_submitted():
        form.proyectos.data = [p.id for p in usuario.proyectos]
    return render_template("usuarios/form.html", form=form, usuario=usuario)


@usuarios_bp.route("/<int:usuario_id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.id == current_user.id:
        flash("No puedes eliminar tu propio usuario.", "warning")
        return redirect(url_for("usuarios.index"))
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado.", "info")
    return redirect(url_for("usuarios.index"))
