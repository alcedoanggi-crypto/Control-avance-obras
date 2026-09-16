"""Diagrama de Gantt (cronograma planificado) de las partidas del proyecto activo.

Usa las fechas planificadas de cada partida (fecha_inicio_plan / fecha_fin_plan,
capturadas en el formulario de partida) para dibujar el cronograma con la libreria
frappe-gantt en el frontend. Las partidas sin fechas planificadas no aparecen.
"""
from datetime import timedelta

from flask import Blueprint, render_template, jsonify
from flask_login import login_required

from app.utils import proyecto_actual

cronograma_bp = Blueprint("cronograma", __name__, url_prefix="/cronograma")


@cronograma_bp.route("/")
@login_required
def index():
    proyecto = proyecto_actual()
    if not proyecto:
        return render_template("dashboard/sin_proyecto.html")
    return render_template("cronograma/index.html", proyecto=proyecto)


@cronograma_bp.route("/api/tareas")
@login_required
def tareas():
    proyecto = proyecto_actual()
    if not proyecto:
        return jsonify([])

    datos = []
    for disciplina in proyecto.disciplinas:
        for p in disciplina.partidas:
            if not (p.fecha_inicio_plan and p.fecha_fin_plan):
                continue
            inicio = p.fecha_inicio_plan
            fin = p.fecha_fin_plan
            if fin <= inicio:
                fin = inicio + timedelta(days=1)
            datos.append({
                "id": f"p{p.id}",
                "name": f"{disciplina.nombre} — {p.numero_partida}. {p.descripcion}",
                "start": inicio.isoformat(),
                "end": fin.isoformat(),
                "progress": round(min(float(p.porcentaje_avance) * 100, 100), 1),
                "custom_class": p.semaforo,
            })
    return jsonify(datos)
