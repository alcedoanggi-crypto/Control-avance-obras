"""CRUD de partidas (presupuesto) dentro de una disciplina. Solo Administrador.

El administrador es el unico que puede tocar cantidad_presupuestada y precio_unitario
(regla de negocio del criterio de aceptacion #3). El modal de partidas/index.html tambien
incluye un slider de %Avance (seccion 3.1: "el usuario solo ingresa %Avance y el sistema
recalcula todo lo demas") que este controlador traduce a cantidad_ejecutada; cada cambio
queda igualmente registrado en historial_avance para no romper la auditoria ni la Curva S.
La pantalla dedicada de campo (app/controllers/avance.py), con evidencia fotografica, sigue
siendo el flujo normal para Supervisor -- este es un atajo adicional solo para Administrador.

Crear/editar tambien se pueden invocar desde el modal de partidas/index.html: si la
peticion llega por fetch() (header X-Requested-With) se responde JSON en vez de redirigir,
para que el modal se quede abierto y muestre los errores de validacion sin recargar la pagina.
"""
from decimal import Decimal

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user

from app.controllers import admin_required
from app.extensions import db
from app.models.disciplina import Disciplina
from app.models.partida import Partida
from app.models.historial_avance import HistorialAvance
from app.forms import PartidaForm
from app.services import reportes as rpt

partidas_bp = Blueprint("partidas", __name__, url_prefix="/disciplinas")


def _es_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _registrar_avance_si_cambio(partida, cantidad_anterior):
    """Crea un HistorialAvance si cantidad_ejecutada cambio via el modal de partida."""
    if partida.cantidad_ejecutada == cantidad_anterior:
        return
    db.session.add(HistorialAvance(
        partida_id=partida.id,
        fecha_corte=partida.disciplina.proyecto.fecha_corte,
        cantidad_ejecutada=partida.cantidad_ejecutada,
        usuario_id=current_user.id,
    ))


@partidas_bp.route("/<int:disciplina_id>/partidas")
@login_required
@admin_required
def index(disciplina_id):
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    return render_template("partidas/index.html", disciplina=disciplina, csrf_form=PartidaForm())


@partidas_bp.route("/<int:disciplina_id>/partidas/nueva", methods=["GET", "POST"])
@login_required
@admin_required
def nueva(disciplina_id):
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    form = PartidaForm()
    if form.validate_on_submit():
        partida = Partida(disciplina_id=disciplina.id,
                          numero_partida=disciplina.siguiente_numero_partida)
        form.populate_obj(partida)
        partida.cantidad_ejecutada = form.cantidad_ejecutada.data or Decimal("0")
        partida.avance_costo_empresa = form.avance_costo_empresa.data or Decimal("0")
        db.session.add(partida)
        db.session.flush()
        _registrar_avance_si_cambio(partida, Decimal("0"))
        db.session.commit()
        if _es_ajax():
            return jsonify(ok=True, redirect=url_for("partidas.index", disciplina_id=disciplina.id))
        flash("Partida creada.", "success")
        return redirect(url_for("partidas.index", disciplina_id=disciplina.id))
    if _es_ajax():
        return jsonify(ok=False, errors=form.errors), 400
    return render_template("partidas/form.html", form=form, disciplina=disciplina, partida=None)


@partidas_bp.route("/partidas/<int:partida_id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar(partida_id):
    partida = Partida.query.get_or_404(partida_id)
    form = PartidaForm(obj=partida)
    if form.validate_on_submit():
        cantidad_anterior = partida.cantidad_ejecutada
        form.populate_obj(partida)
        partida.cantidad_ejecutada = form.cantidad_ejecutada.data or Decimal("0")
        partida.avance_costo_empresa = form.avance_costo_empresa.data or Decimal("0")
        _registrar_avance_si_cambio(partida, cantidad_anterior)
        db.session.commit()
        if _es_ajax():
            return jsonify(ok=True, redirect=url_for("partidas.index", disciplina_id=partida.disciplina_id))
        flash("Partida actualizada.", "success")
        return redirect(url_for("partidas.index", disciplina_id=partida.disciplina_id))
    if _es_ajax():
        return jsonify(ok=False, errors=form.errors), 400
    return render_template("partidas/form.html", form=form, disciplina=partida.disciplina,
                           partida=partida)


@partidas_bp.route("/<int:disciplina_id>/partidas/pdf")
@login_required
@admin_required
def pdf(disciplina_id):
    disciplina = Disciplina.query.get_or_404(disciplina_id)
    buffer, ext = rpt.reporte_partidas_disciplina(disciplina)
    return send_file(
        buffer, mimetype="application/pdf", as_attachment=True,
        download_name=f"partidas_{disciplina.id}.{ext}",
    )


@partidas_bp.route("/partidas/<int:partida_id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar(partida_id):
    partida = Partida.query.get_or_404(partida_id)
    disciplina_id = partida.disciplina_id
    db.session.delete(partida)
    db.session.commit()
    flash("Partida eliminada.", "info")
    return redirect(url_for("partidas.index", disciplina_id=disciplina_id))
