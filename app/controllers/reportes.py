"""Reportes exportables en PDF / Excel del proyecto activo."""
from flask import Blueprint, render_template, send_file, abort
from flask_login import login_required, current_user

from app.services import reportes as rpt
from app.utils import proyecto_actual

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")

MIME = {
    "pdf": "application/pdf",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


@reportes_bp.route("/")
@login_required
def index():
    proyecto = proyecto_actual()
    if not proyecto:
        return render_template("dashboard/sin_proyecto.html")
    return render_template("reportes/index.html", proyecto=proyecto)


@reportes_bp.route("/avance.<formato>")
@login_required
def generar(formato):
    if formato not in ("pdf", "excel"):
        abort(404)
    proyecto = proyecto_actual()
    if not proyecto:
        abort(404)

    buffer, ext = rpt.reporte_avance(proyecto, formato, ocultar_precios=current_user.es_cliente)
    return send_file(
        buffer, mimetype=MIME[ext], as_attachment=True,
        download_name=f"avance_obra_{proyecto.id}.{ext}",
    )
