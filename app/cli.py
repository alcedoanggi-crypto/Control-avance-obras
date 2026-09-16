"""Comandos de linea de comandos: crear tablas y cargar datos de ejemplo."""
from datetime import date, timedelta
from decimal import Decimal

import click
from flask import current_app

from app.extensions import db


def register_cli(app):
    app.cli.add_command(init_db)
    app.cli.add_command(seed)


@click.command("init-db")
def init_db():
    """Crea todas las tablas en la base de datos configurada."""
    db.create_all()
    click.echo("Tablas creadas.")


@click.command("seed")
@click.option("--reset", is_flag=True, help="Borra y recrea las tablas antes de sembrar.")
def seed(reset):
    """Carga el proyecto de ejemplo 'Penthouse Res. Atamaica, El Cafetal'."""
    from app.models.usuario import Usuario, RolUsuario
    from app.models.proyecto import Proyecto
    from app.models.disciplina import Disciplina
    from app.models.partida import Partida
    from app.models.historial_avance import HistorialAvance

    if reset:
        db.drop_all()
        click.echo("Tablas eliminadas.")
    db.create_all()

    if Usuario.query.first():
        click.echo("Ya hay datos. Usa --reset para reiniciar.")
        return

    # -- Usuarios ----------------------------------------------------------
    admin = Usuario(nombre="Anngi", apellido="Administradora", email="admin@atamaica.com",
                    rol=RolUsuario.ADMIN)
    admin.set_password("admin123")

    supervisor = Usuario(nombre="Carlos", apellido="Residente", email="supervisor@atamaica.com",
                        rol=RolUsuario.SUPERVISOR)
    supervisor.set_password("supervisor123")

    cliente = Usuario(nombre="Maria", apellido="Propietaria", email="cliente@atamaica.com",
                      rol=RolUsuario.CLIENTE)
    cliente.set_password("cliente123")

    db.session.add_all([admin, supervisor, cliente])

    # -- Proyecto ------------------------------------------------------------
    fecha_inicio = date(2026, 1, 15)
    fecha_corte = date.today()
    proyecto = Proyecto(
        nombre="Penthouse Res. Atamaica, El Cafetal",
        fecha_inicio=fecha_inicio,
        fecha_fin_estimada=date(2026, 12, 15),
        fecha_corte=fecha_corte,
        activo=True,
    )
    supervisor.proyectos.append(proyecto)
    cliente.proyectos.append(proyecto)
    db.session.add(proyecto)
    db.session.flush()

    # -- Disciplinas y partidas (dataset semilla extraido del Excel origen) --
    datos = [
        {
            "nombre": "Obra Civil y Albañilería",
            "orden": 1, "aplica_iva": True, "iva_porcentaje": Decimal("16"),
            # offset_dias / duracion_dias: para distribuir el cronograma planificado (Gantt) de
            # las partidas de esta disciplina a partir de fecha_inicio del proyecto.
            "offset_dias": 0, "duracion_dias": 165,
            "partidas": [
                ("Demolición y desmontaje", "GLOBAL", 1, 3500, 1),
                ("Movimiento de tierra", "m3", 45, 180, 45),
                ("Estructura de concreto armado", "m3", 60, 420, 38),
                ("Bloques y mampostería", "m2", 320, 28, 100),
                ("Frisos y acabados de paredes", "m2", 480, 22, 0),
                ("Impermeabilización de losa", "m2", 150, 35, 150),
                ("Piso de porcelanato", "m2", 280, 65, 0),
            ],
        },
        {
            "nombre": "Instalaciones Eléctricas",
            "orden": 2, "aplica_iva": False, "iva_porcentaje": Decimal("0"),
            "offset_dias": 70, "duracion_dias": 100,
            "partidas": [
                ("Acometida eléctrica principal", "GLOBAL", 1, 4200, 1),
                ("Tablero de distribución", "UND", 2, 1800, 2),
                ("Cableado y tuberías", "MTS", 850, 12, 500),
                ("Salidas de iluminación", "UND", 65, 45, 20),
                ("Salidas de tomacorrientes", "UND", 90, 38, 0),
            ],
        },
        {
            "nombre": "Instalaciones Mecánicas – Equipos",
            "orden": 3, "aplica_iva": False, "iva_porcentaje": Decimal("0"),
            "offset_dias": 160, "duracion_dias": 55,
            "partidas": [
                ("Unidades tipo Split 18000 BTU", "UND", 4, 950, 4),
                ("Unidad tipo Cassette 24000 BTU", "UND", 2, 1450, 1),
                ("Compresor VRF central", "UND", 1, 8500, 0),
            ],
        },
        {
            "nombre": "Instalaciones Mecánicas – Materiales y Mano de Obra",
            "orden": 4, "aplica_iva": False, "iva_porcentaje": Decimal("0"),
            "offset_dias": 150, "duracion_dias": 120,
            "partidas": [
                ("Tubería de cobre y accesorios", "MTS", 180, 22, 200),
                ("Bomba de condensado", "UND", 6, 210, 6),
                ("Aislamiento térmico de tubería", "MTS", 180, 8, 90),
                ("Mano de obra de instalación", "GLOBAL", 1, 3200, Decimal("0.4")),
            ],
        },
    ]

    for bloque in datos:
        disciplina = Disciplina(
            proyecto_id=proyecto.id, nombre=bloque["nombre"], orden=bloque["orden"],
            aplica_iva=bloque["aplica_iva"], iva_porcentaje=bloque["iva_porcentaje"],
        )
        db.session.add(disciplina)
        db.session.flush()

        total_partidas = len(bloque["partidas"])
        paso = bloque["duracion_dias"] / total_partidas

        for indice, (descripcion, unidad, cant_presup, precio, cant_ejec) in enumerate(
            bloque["partidas"]
        ):
            numero = indice + 1
            inicio_plan = fecha_inicio + timedelta(days=bloque["offset_dias"] + int(indice * paso * 0.75))
            fin_plan = inicio_plan + timedelta(days=max(int(paso * 1.3), 7))
            partida = Partida(
                disciplina_id=disciplina.id, numero_partida=numero, descripcion=descripcion,
                unidad=unidad, cantidad_presupuestada=Decimal(str(cant_presup)),
                precio_unitario=Decimal(str(precio)), cantidad_ejecutada=Decimal(str(cant_ejec)),
                fecha_inicio_plan=inicio_plan, fecha_fin_plan=fin_plan,
            )
            db.session.add(partida)
            db.session.flush()

            # Historial de avance: dos cortes previos para poder graficar la curva S.
            if cant_ejec:
                avance_previo = Decimal(str(cant_ejec)) * Decimal("0.55")
                db.session.add(HistorialAvance(
                    partida_id=partida.id, fecha_corte=fecha_corte - timedelta(days=45),
                    cantidad_ejecutada=avance_previo.quantize(Decimal("0.01")),
                    usuario_id=supervisor.id,
                ))
                db.session.add(HistorialAvance(
                    partida_id=partida.id, fecha_corte=fecha_corte - timedelta(days=10),
                    cantidad_ejecutada=Decimal(str(cant_ejec)), usuario_id=supervisor.id,
                ))

    db.session.commit()

    click.echo("Datos de ejemplo cargados.")
    click.echo("  Admin      : admin@atamaica.com / admin123")
    click.echo("  Supervisor : supervisor@atamaica.com / supervisor123")
    click.echo("  Cliente    : cliente@atamaica.com / cliente123")
