"""Historial de avance: snapshot de cada actualizacion de cantidad_ejecutada.

Sirve como (1) registro de auditoria (quien actualizo que partida y cuando),
y (2) fuente de datos para la curva S (avance acumulado en el tiempo).
"""
from datetime import datetime

from app.extensions import db


class HistorialAvance(db.Model):
    __tablename__ = "historial_avance"

    id = db.Column(db.Integer, primary_key=True)
    partida_id = db.Column(db.Integer, db.ForeignKey("partidas.id"), nullable=False)
    fecha_corte = db.Column(db.Date, nullable=False)
    cantidad_ejecutada = db.Column(db.Numeric(14, 2), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    evidencia_url = db.Column(db.String(255), nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    partida = db.relationship("Partida", back_populates="historial")
    usuario = db.relationship("Usuario", back_populates="actualizaciones")

    @property
    def monto_ejecutado(self):
        return self.cantidad_ejecutada * self.partida.precio_unitario

    def __repr__(self):
        return f"<HistorialAvance partida={self.partida_id} corte={self.fecha_corte}>"
