"""Modelo Proyecto (obra)."""
from datetime import date, datetime
from decimal import Decimal

from app.extensions import db

usuarios_proyectos = db.Table(
    "usuarios_proyectos",
    db.Column("usuario_id", db.Integer, db.ForeignKey("usuarios.id"), primary_key=True),
    db.Column("proyecto_id", db.Integer, db.ForeignKey("proyectos.id"), primary_key=True),
)


class Proyecto(db.Model):
    __tablename__ = "proyectos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False, default=date.today)
    fecha_fin_estimada = db.Column(db.Date, nullable=True)
    fecha_corte = db.Column(db.Date, nullable=False, default=date.today)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    disciplinas = db.relationship(
        "Disciplina", back_populates="proyecto",
        order_by="Disciplina.orden", cascade="all, delete-orphan",
    )
    usuarios = db.relationship(
        "Usuario", secondary=usuarios_proyectos, back_populates="proyectos",
    )

    # -- agregados calculados (no se persisten) ---------------------------
    @property
    def monto_total(self):
        """Suma de los subtotales presupuestados (sin IVA) de cada disciplina."""
        return sum((d.subtotal_presupuestado for d in self.disciplinas), Decimal(0))

    @property
    def monto_total_con_iva(self):
        return sum((d.total_con_iva for d in self.disciplinas), Decimal(0))

    @property
    def monto_ejecutado_total(self):
        return sum((d.monto_ejecutado for d in self.disciplinas), Decimal(0))

    @property
    def avance_financiero(self):
        total = self.monto_total
        return (self.monto_ejecutado_total / total) if total else Decimal(0)

    @property
    def dias_transcurridos(self):
        return (date.today() - self.fecha_inicio).days if self.fecha_inicio else 0

    @property
    def partidas(self):
        return [p for d in self.disciplinas for p in d.partidas]

    @property
    def partidas_sobre_ejecutadas(self):
        return [p for p in self.partidas if p.sobre_ejecutada]

    @property
    def peso_ponderado_total(self):
        """Validacion de integridad: debe sumar ~1 (100%) entre todas las disciplinas."""
        total = self.monto_total
        if not total:
            return Decimal(0)
        return sum((d.subtotal_presupuestado for d in self.disciplinas), Decimal(0)) / total

    def __repr__(self):
        return f"<Proyecto {self.nombre}>"
