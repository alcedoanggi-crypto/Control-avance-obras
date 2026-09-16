"""Modelo Partida (linea de presupuesto). Tabla central del sistema.

Formulas (ver seccion 3 del prompt tecnico), calculadas en backend, nunca en el frontend:
  total_presupuestado = cantidad_presupuestada * precio_unitario
  peso_ponderado       = total_presupuestado / SUBTOTAL_disciplina
  monto_ejecutado      = cantidad_ejecutada * precio_unitario
  porcentaje_avance    = monto_ejecutado / total_presupuestado (avance propio de la partida,
                         usado para el semaforo; no se divide entre el subtotal de la disciplina
                         porque ese cociente casi nunca se acerca a 100% y rompe el semaforo)

Modulo de Valuacion (seccion 3.1 del prompt tecnico). Se deriva siempre de porcentaje_avance;
el usuario nunca lo edita directamente:
  valuacion_total       = total_presupuestado * porcentaje_avance
  valuacion_pendiente   = total_presupuestado - valuacion_total

Modulo de Costo empresa: el frontend precarga avance_costo_empresa con el mismo valor del
%Avance de ejecucion cada vez que este cambia, pero el usuario puede sobrescribirlo a mano
(p. ej. 30% o 100% segun lo que la empresa ya pago/gasto de esa partida) cuando el gasto real
difiere del avance fisico. El valor guardado no se deriva de cantidad_ejecutada en backend.
gastado_empresa se deriva solo de avance_costo_empresa (no del porcentaje_avance de arriba):
  costo_empresa          = total_presupuestado
  gastado_empresa        = costo_empresa * (avance_costo_empresa / 100)
  resta_por_gastar_empresa = costo_empresa - gastado_empresa
  utilidad_empresa       = total_presupuestado - gastado_empresa
"""
from datetime import datetime
from decimal import Decimal

from app.extensions import db


class Partida(db.Model):
    __tablename__ = "partidas"

    id = db.Column(db.Integer, primary_key=True)
    disciplina_id = db.Column(db.Integer, db.ForeignKey("disciplinas.id"), nullable=False)
    numero_partida = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)
    cantidad_presupuestada = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("0"))
    precio_unitario = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("0"))
    cantidad_ejecutada = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("0"))
    avance_costo_empresa = db.Column(db.Numeric(5, 2), nullable=False, default=Decimal("0"))
    fecha_inicio_plan = db.Column(db.Date, nullable=True)
    fecha_fin_plan = db.Column(db.Date, nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow,
                               onupdate=datetime.utcnow)

    disciplina = db.relationship("Disciplina", back_populates="partidas")
    historial = db.relationship(
        "HistorialAvance", back_populates="partida",
        order_by="HistorialAvance.fecha_corte, HistorialAvance.id",
        cascade="all, delete-orphan",
    )

    # -- formulas -----------------------------------------------------------
    @property
    def total_presupuestado(self):
        return (self.cantidad_presupuestada or Decimal(0)) * (self.precio_unitario or Decimal(0))

    @property
    def monto_ejecutado(self):
        return (self.cantidad_ejecutada or Decimal(0)) * (self.precio_unitario or Decimal(0))

    @property
    def peso_ponderado(self):
        subtotal = self.disciplina.subtotal_presupuestado if self.disciplina else Decimal(0)
        if not subtotal:
            return Decimal(0)
        return self.total_presupuestado / subtotal

    @property
    def porcentaje_avance(self):
        if not self.cantidad_presupuestada:
            return Decimal(0)
        return self.cantidad_ejecutada / self.cantidad_presupuestada

    # -- modulo de valuacion (seccion 3.1) -----------------------------------
    @property
    def valuacion_total(self):
        return self.total_presupuestado * self.porcentaje_avance

    @property
    def valuacion_pendiente(self):
        return self.total_presupuestado - self.valuacion_total

    # -- modulo de costo empresa ---------------------------------------------
    @property
    def costo_empresa(self):
        return self.total_presupuestado

    @property
    def gastado_empresa(self):
        avance_costo_frac = (self.avance_costo_empresa or Decimal(0)) / Decimal(100)
        return self.costo_empresa * avance_costo_frac

    @property
    def resta_por_gastar_empresa(self):
        return self.costo_empresa - self.gastado_empresa

    @property
    def utilidad_empresa(self):
        return self.total_presupuestado - self.gastado_empresa

    @property
    def sobre_ejecutada(self):
        return self.cantidad_ejecutada > self.cantidad_presupuestada

    @property
    def semaforo(self):
        pct = float(self.porcentaje_avance) * 100
        if pct >= 80:
            return "verde"
        if pct >= 40:
            return "amarillo"
        return "rojo"

    @property
    def ultima_actualizacion(self):
        return self.historial[-1].creado_en if self.historial else self.creado_en

    @property
    def dias_sin_actualizar(self):
        return (datetime.utcnow() - self.ultima_actualizacion).days

    def __repr__(self):
        return f"<Partida {self.numero_partida} {self.descripcion[:30]!r}>"
