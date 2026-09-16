"""Actualizacion rapida de campo (cantidad_ejecutada) y su historial de auditoria.

Disponible para Administrador y Supervisor. El Supervisor solo puede actualizar
cantidad_ejecutada -- nunca cantidad_presupuestada ni precio_unitario, que se
gestionan exclusivamente desde app/controllers/partidas.py (Administrador).
"""
import os
from uuid import uuid4

from flask import Blueprint, render_template, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user

from app.controllers import gestion_avance_required
from app.extensions import db
from app.models.disciplina import Disciplina
from app.models.partida import Partida
from app.models.historial_avance import HistorialAvance
from app.forms import AvanceForm
from app.utils import proyecto_actual

avance_bp = Blueprint("avance", __name__, url_prefix="/avance")


def _guardar_evidencia(archivo):
    if not archivo or not archivo.filename:
        return None
    ext = archivo.filename.rsplit(".", 1)[-1].lower()
    nombre = f"{uuid4().hex}.{ext}"
    ruta = os.path.join(current_app.config["UPLOAD_FOLDER"], nombre)
    archivo.save(ruta)
    return f"uploads/evidencias/{nombre}"


@avance_bp.route("/")
@login_required
@gestion_avance_required
def index():
    proyecto = proyecto_actual()
    if not proyecto:
        return render_template("dashboard/sin_proyecto.html")
    form = AvanceForm()
    return render_template("avance/index.html", proyecto=proyecto, form=form)


@avance_bp.route("/partida/<int:partida_id>", methods=["POST"])
@login_required
@gestion_avance_required
def actualizar(partida_id):
    partida = Partida.query.get_or_404(partida_id)
    if not current_user.tiene_acceso(partida.disciplina.proyecto):
        abort(403)

    form = AvanceForm()
    if form.validate_on_submit():
        evidencia_url = _guardar_evidencia(form.evidencia.data)
        partida.cantidad_ejecutada = form.cantidad_ejecutada.data
        db.session.add(HistorialAvance(
            partida_id=partida.id,
            fecha_corte=form.fecha_corte.data,
            cantidad_ejecutada=form.cantidad_ejecutada.data,
            usuario_id=current_user.id,
            evidencia_url=evidencia_url,
        ))
        db.session.commit()
        flash(f"Avance de la partida {partida.numero_partida} actualizado.", "success")
    else:
        for errores in form.errors.values():
            for e in errores:
                flash(e, "danger")
    return redirect(url_for("avance.index"))


@avance_bp.route("/historial")
@login_required
def historial():
    proyecto = proyecto_actual()
    if not proyecto:
        return render_template("dashboard/sin_proyecto.html")
    registros = (
        HistorialAvance.query
        .join(Partida, HistorialAvance.partida_id == Partida.id)
        .join(Disciplina, Partida.disciplina_id == Disciplina.id)
        .filter(Disciplina.proyecto_id == proyecto.id)
        .order_by(HistorialAvance.fecha_corte.desc(), HistorialAvance.id.desc())
        .all()
    )
    return render_template("avance/historial.html", proyecto=proyecto, registros=registros)
