"""Gestion de proyectos (obras) y sus disciplinas. Solo Administrador."""
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required

from app.controllers import admin_required
from app.extensions import db
from app.models.proyecto import Proyecto
from app.models.disciplina import Disciplina
from app.forms import ProyectoForm, DisciplinaForm

proyectos_bp = Blueprint("proyectos", __name__, url_prefix="/proyectos")


@proyectos_bp.route("/")
@login_required
@admin_required
def index():
    proyectos = Proyecto.query.order_by(Proyecto.nombre).all()
    return render_template("proyectos/index.html", proyectos=proyectos)


@proyectos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@admin_required
def nuevo():
    form = ProyectoForm()
    if form.validate_on_submit():
        proyecto = Proyecto()
        form.populate_obj(proyecto)
        db.session.add(proyecto)
        db.session.commit()
        flash("Proyecto creado.", "success")
        return redirect(url_for("proyectos.detalle", proyecto_id=proyecto.id))
    return render_template("proyectos/form.html", form=form, proyecto=None)


@proyectos_bp.route("/<int:proyecto_id>")
@login_required
@admin_required
def detalle(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)
    return render_template("proyectos/detalle.html", proyecto=proyecto)


@proyectos_bp.route("/<int:proyecto_id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)
    form = ProyectoForm(obj=proyecto)
    if form.validate_on_submit():
        form.populate_obj(proyecto)
        db.session.commit()
        flash("Proyecto actualizado.", "success")
        return redirect(url_for("proyectos.detalle", proyecto_id=proyecto.id))
    return render_template("proyectos/form.html", form=form, proyecto=proyecto)


@proyectos_bp.route("/<int:proyecto_id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)
    db.session.delete(proyecto)
    db.session.commit()
    flash("Proyecto eliminado.", "info")
    return redirect(url_for("proyectos.index"))


# -- Disciplinas (anidadas a un proyecto) ------------------------------------
@proyectos_bp.route("/<int:proyecto_id>/disciplinas/nueva", methods=["GET", "POST"])
@login_required
@admin_required
def nueva_disciplina(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)
    form = DisciplinaForm()
    if form.validate_on_submit():
        disciplina = Disciplina(proyecto_id=proyecto.id)
        form.populate_obj(disciplina)
        db.session.add(disciplina)
        db.session.commit()
        flash("Disciplina creada.", "success")
        return redirect(url_for("proyectos.detalle", proyecto_id=proyecto.id))
    return render_template("disciplinas/form.html", form=form, proyecto=proyecto, disciplina=None)


@proyectos_bp.route("/disciplinas/<int:disciplina_id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar_disciplina(disciplina_id):
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    form = DisciplinaForm(obj=disciplina)
    if form.validate_on_submit():
        form.populate_obj(disciplina)
        db.session.commit()
        flash("Disciplina actualizada.", "success")
        return redirect(url_for("proyectos.detalle", proyecto_id=disciplina.proyecto_id))
    return render_template("disciplinas/form.html", form=form, proyecto=disciplina.proyecto,
                           disciplina=disciplina)


@proyectos_bp.route("/disciplinas/<int:disciplina_id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar_disciplina(disciplina_id):
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    proyecto_id = disciplina.proyecto_id
    db.session.delete(disciplina)
    db.session.commit()
    flash("Disciplina eliminada.", "info")
    return redirect(url_for("proyectos.detalle", proyecto_id=proyecto_id))
