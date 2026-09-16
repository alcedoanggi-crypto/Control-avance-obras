"""Modelo Disciplina (bloque/seccion de partidas dentro de un proyecto)."""
from decimal import Decimal

from app.extensions import db


class Disciplina(db.Model):
    __tablename__ = "disciplinas"

    id = db.Column(db.Integer, primary_key=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    orden = db.Column(db.Integer, nullable=False, default=0)
    aplica_iva = db.Column(db.Boolean, nullable=False, default=False)
    iva_porcentaje = db.Column(db.Numeric(5, 2), nullable=False, default=Decimal("0"))

    proyecto = db.relationship("Proyecto", back_populates="disciplinas")
    partidas = db.relationship(
        "Partida", back_populates="disciplina",
        order_by="Partida.numero_partida", cascade="all, delete-orphan",
    )

    # -- agregados calculados (formulas del Excel, seccion 3) --------------
    @property
    def subtotal_presupuestado(self):
        return sum((p.total_presupuestado for p in self.partidas), Decimal(0))

    @property
    def monto_ejecutado(self):
        return sum((p.monto_ejecutado for p in self.partidas), Decimal(0))

    @property
    def avance(self):
        subtotal = self.subtotal_presupuestado
        return (self.monto_ejecutado / subtotal) if subtotal else Decimal(0)

    @property
    def iva_monto(self):
        if not self.aplica_iva:
            return Decimal(0)
        return self.subtotal_presupuestado * (self.iva_porcentaje / Decimal(100))

    @property
    def total_con_iva(self):
        return self.subtotal_presupuestado + self.iva_monto

    @property
    def peso_ponderado_total(self):
        """Validacion de integridad: debe sumar ~1 (100%) dentro de la disciplina."""
        return sum((p.peso_ponderado for p in self.partidas), Decimal(0))

    # -- modulo de valuacion (seccion 3.1) -----------------------------------
    @property
    def valuacion_total(self):
        return sum((p.valuacion_total for p in self.partidas), Decimal(0))

    @property
    def valuacion_pendiente_total(self):
        return sum((p.valuacion_pendiente for p in self.partidas), Decimal(0))

    # -- modulo de costo empresa ---------------------------------------------
    @property
    def gastado_empresa_total(self):
        return sum((p.gastado_empresa for p in self.partidas), Decimal(0))

    @property
    def resta_por_gastar_empresa_total(self):
        return sum((p.resta_por_gastar_empresa for p in self.partidas), Decimal(0))

    @property
    def utilidad_empresa_total(self):
        return sum((p.utilidad_empresa for p in self.partidas), Decimal(0))

    @property
    def siguiente_numero_partida(self):
        numeros = [p.numero_partida for p in self.partidas]
        return (max(numeros) + 1) if numeros else 1

    def __repr__(self):
        return f"<Disciplina {self.nombre}>"
