"""Formularios WTForms."""
from decimal import Decimal

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, SelectField, SelectMultipleField,
    IntegerField, TextAreaField, BooleanField, DateField, DecimalField,
)
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from wtforms.widgets import TextInput

from app.models.usuario import RolUsuario


class DecimalComaField(DecimalField):
    """DecimalField que acepta coma o punto como separador decimal
    (p. ej. "3,5" o "3.5"), para no forzar el formato anglosajon en
    montos de dinero (dolares, bolivares u otra moneda)."""
    widget = TextInput()

    def process_formdata(self, valuelist):
        if valuelist:
            valuelist = [str(valuelist[0]).strip().replace(",", ".")]
        super().process_formdata(valuelist)


class LoginForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password = PasswordField("Contrasena", validators=[DataRequired()])
    recordarme = BooleanField("Recordarme")


class ProyectoForm(FlaskForm):
    nombre = StringField("Nombre de la obra", validators=[DataRequired(), Length(max=150)])
    fecha_inicio = DateField("Fecha de inicio", validators=[DataRequired()])
    fecha_fin_estimada = DateField("Fecha fin estimada", validators=[Optional()])
    fecha_corte = DateField("Fecha de corte actual", validators=[DataRequired()])
    activo = BooleanField("Activo", default=True)


class DisciplinaForm(FlaskForm):
    nombre = StringField("Nombre de la disciplina", validators=[DataRequired(), Length(max=150)])
    orden = IntegerField("Orden", validators=[Optional(), NumberRange(min=0)], default=0)
    aplica_iva = BooleanField("Aplica IVA")
    iva_porcentaje = DecimalComaField("IVA (%)", validators=[Optional(), NumberRange(min=0, max=100)],
                                       default=0, places=2)


class PartidaForm(FlaskForm):
    descripcion = TextAreaField("Descripcion de partida", validators=[DataRequired()])
    unidad = StringField("Unidad", validators=[DataRequired(), Length(max=20)])
    cantidad_presupuestada = DecimalComaField("Cantidad presupuestada",
                                              validators=[DataRequired(), NumberRange(min=0)], places=2)
    precio_unitario = DecimalComaField("Precio unitario ($)",
                                       validators=[DataRequired(), NumberRange(min=0)], places=2)
    fecha_inicio_plan = DateField("Fecha inicio planificada (cronograma)", validators=[Optional()])
    fecha_fin_plan = DateField("Fecha fin planificada (cronograma)", validators=[Optional()])
    # Se llena desde el slider de %Avance del modal (JS calcula cantidad = cantidad_presupuestada
    # * avance/100). Opcional porque el flujo principal de campo sigue siendo AvanceForm/avance.py.
    cantidad_ejecutada = DecimalComaField("Cantidad ejecutada", validators=[Optional(), NumberRange(min=0)],
                                          places=2)
    # Avance manual del modulo de Costo empresa (seccion "Costo empresa"): independiente
    # del %Avance de ejecucion de arriba, lo escribe el usuario a mano (ej. 30% o 100%).
    avance_costo_empresa = DecimalComaField("Avance costo empresa (%)",
                                            validators=[Optional(), NumberRange(min=0, max=100)],
                                            places=2, default=Decimal("0"))


class AvanceForm(FlaskForm):
    cantidad_ejecutada = DecimalComaField("Cantidad ejecutada", validators=[DataRequired(), NumberRange(min=0)],
                                          places=2)
    fecha_corte = DateField("Fecha de corte", validators=[DataRequired()])
    evidencia = FileField("Evidencia fotografica",
                          validators=[Optional(), FileAllowed(["png", "jpg", "jpeg", "webp"], "Solo imagenes.")])


class UsuarioForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=80)])
    apellido = StringField("Apellido", validators=[DataRequired(), Length(max=80)])
    email = StringField("Correo", validators=[DataRequired(), Email(), Length(max=120)])
    rol = SelectField("Rol", choices=[(r, RolUsuario.ETIQUETAS[r]) for r in RolUsuario.OPCIONES])
    activo = BooleanField("Activo", default=True)
    proyectos = SelectMultipleField("Proyectos con acceso", coerce=int, validators=[Optional()])
    password = PasswordField("Contrasena (dejar vacio para no cambiar)",
                             validators=[Optional(), Length(min=6)])
