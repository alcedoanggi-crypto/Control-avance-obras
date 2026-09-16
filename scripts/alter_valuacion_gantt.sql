-- Agrega a la tabla partidas los campos del cronograma planificado (Gantt) y del
-- modulo de Valuacion / Costo Empresa / Utilidad (seccion 3.1). No destructivo:
-- conserva las filas existentes; las columnas nuevas quedan NULL o con su default.
ALTER TABLE partidas
    ADD COLUMN IF NOT EXISTS fecha_inicio_plan DATE,
    ADD COLUMN IF NOT EXISTS fecha_fin_plan DATE,
    ADD COLUMN IF NOT EXISTS margen_costo_empresa NUMERIC(5, 2) NOT NULL DEFAULT 70;
