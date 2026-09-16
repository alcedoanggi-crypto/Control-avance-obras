"""Autenticacion: login y logout. Los usuarios los crea el administrador."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.models.usuario import Usuario
from app.forms import LoginForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data.lower().strip()).first()
        if usuario and usuario.check_password(form.password.data):
            if not usuario.activo:
                flash("Tu cuenta esta desactivada. Contacta al administrador.", "danger")
                return render_template("auth/login.html", form=form)
            login_user(usuario, remember=form.recordarme.data)
            flash(f"Bienvenido, {usuario.nombre}.", "success")
            destino = request.args.get("next")
            return redirect(destino or url_for("dashboard.index"))
        flash("Correo o contrasena incorrectos.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesion cerrada.", "info")
    return redirect(url_for("auth.login"))
