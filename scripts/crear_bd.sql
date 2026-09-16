CREATE DATABASE control_avance_obra;

DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'avance_app') THEN
      CREATE ROLE avance_app LOGIN PASSWORD 'avance_pass';
   END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE control_avance_obra TO avance_app;

\connect control_avance_obra

GRANT ALL ON SCHEMA public TO avance_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO avance_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO avance_app;
