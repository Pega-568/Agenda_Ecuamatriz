-- ============================================================
-- docker/postgres/init.sql
-- Script de inicialización de PostgreSQL
-- Se ejecuta UNA SOLA VEZ cuando el contenedor se crea por primera vez.
-- ============================================================

-- Crear base de datos de pruebas (para pytest)
-- La BD principal 'agenda_ecuamatriz' ya la crea POSTGRES_DB en docker-compose.yml
SELECT 'CREATE DATABASE agenda_ecuamatriz_test OWNER agenda_user'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'agenda_ecuamatriz_test'
)\gexec

-- Otorgar privilegios completos al usuario en la BD de test
GRANT ALL PRIVILEGES ON DATABASE agenda_ecuamatriz_test TO agenda_user;
