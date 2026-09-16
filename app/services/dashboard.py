"""Consultas agregadas para el dashboard y sus graficos (Chart.js)."""
from datetime import date, datetime, timedelta
from decimal import Decimal

from flask import current_app


def kpis(proyecto):
    return {
        "monto_total": float(proyecto.monto_total_con_iva),
        "monto_ejecutado": float(proyecto.monto_ejecutado_total),
        "avance_financiero": float(proyecto.avance_financiero) * 100,
        "dias_transcurridos": proyecto.dias_transcurridos,
        "sobre_ejecutadas": len(proyecto.partidas_sobre_ejecutadas),
    }


def avance_por_disciplina(proyecto):
    disciplinas = proyecto.disciplinas
    return {
        "labels": [d.nombre for d in disciplinas],
        "presupuestado": [float(d.subtotal_presupuestado) for d in disciplinas],
        "ejecutado": [float(d.monto_ejecutado) for d in disciplinas],
    }


def peso_por_disciplina(proyecto):
    total = proyecto.monto_total
    disciplinas = proyecto.disciplinas
    return {
        "labels": [d.nombre for d in disciplinas],
        "data": [
            round(float(d.subtotal_presupuestado) / float(total) * 100, 2) if total else 0
            for d in disciplinas
        ],
    }


def top_partidas_peso(proyecto, limite=10):
    partidas = sorted(proyecto.partidas, key=lambda p: p.peso_ponderado, reverse=True)[:limite]
    ejecutado_pct = []
    pendiente_pct = []
    for p in partidas:
        pct = float(p.porcentaje_avance) * 100
        ejecutado_pct.append(round(min(pct, 100), 1))
        pendiente_pct.append(round(max(100 - pct, 0), 1))
    return {
        "labels": [f"{p.numero_partida}. {p.descripcion[:32]}" for p in partidas],
        "ejecutado_pct": ejecutado_pct,
        "pendiente_pct": pendiente_pct,
    }


def curva_s(proyecto):
    """Avance financiero acumulado: planificado (lineal) vs. real (segun historial_avance)."""
    partidas = proyecto.partidas
    monto_total = float(proyecto.monto_total)

    fechas = sorted({h.fecha_corte for p in partidas for h in p.historial})
    if not fechas or fechas[0] != proyecto.fecha_inicio:
        fechas = [proyecto.fecha_inicio] + fechas

    fecha_fin = proyecto.fecha_fin_estimada or proyecto.fecha_corte or date.today()
    duracion = (fecha_fin - proyecto.fecha_inicio).days or 1

    real = []
    planificado = []
    for f in fechas:
        acumulado = 0.0
        for p in partidas:
            previas = [h for h in p.historial if h.fecha_corte <= f]
            if previas:
                ultima = max(previas, key=lambda h: (h.fecha_corte, h.id))
                acumulado += float(ultima.cantidad_ejecutada) * float(p.precio_unitario)
        real.append(round(acumulado, 2))

        dias = min(max((f - proyecto.fecha_inicio).days, 0), duracion)
        planificado.append(round(monto_total * dias / duracion, 2))

    return {
        "labels": [f.strftime("%d/%m/%Y") for f in fechas],
        "real": real,
        "planificado": planificado,
    }


def partidas_sin_actualizar(proyecto):
    dias_alerta = current_app.config["DIAS_ALERTA_SIN_ACTUALIZAR"]
    return [p for p in proyecto.partidas if p.dias_sin_actualizar >= dias_alerta]
