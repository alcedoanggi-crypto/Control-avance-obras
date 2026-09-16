"""Dashboard con KPIs y datos para los graficos Chart.js."""
from flask import Blueprint, render_template, jsonify, redirect, url_for, session, abort
from flask_login import login_required, current_user

from app.services import dashboard as svc
from app.utils import proyecto_actual, proyectos_accesibles

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    proyecto = proyecto_actual()
    if not proyecto:
        return render_template("dashboard/sin_proyecto.html")

    contexto = {
        "proyecto": proyecto,
        "kpis": svc.kpis(proyecto),
        "sobre_ejecutadas": proyecto.partidas_sobre_ejecutadas,
        "sin_actualizar": svc.partidas_sin_actualizar(proyecto),
        "ocultar_precios": current_user.es_cliente,
    }
    return render_template("dashboard/index.html", **contexto)


@dashboard_bp.route("/proyecto/<int:proyecto_id>/seleccionar")
@login_required
def seleccionar_proyecto(proyecto_id):
    proyectos = proyectos_accesibles()
    if not any(p.id == proyecto_id for p in proyectos):
        abort(403)
    session["proyecto_id"] = proyecto_id
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/api/dashboard/graficos")
@login_required
def graficos():
    proyecto = proyecto_actual()
    if not proyecto:
        return jsonify({})
    return jsonify({
        "avance_disciplina": svc.avance_por_disciplina(proyecto),
        "peso_disciplina": svc.peso_por_disciplina(proyecto),
        "top_partidas": svc.top_partidas_peso(proyecto),
        "curva_s": svc.curva_s(proyecto),
    })
