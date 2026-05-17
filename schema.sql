-- ============================================================================
-- ARCHIVO: schema.sql
-- PROPÓSITO: Script de inicialización de la base de datos para Agendify.
--
-- DDL (Data Definition Language) es el subconjunto de SQL que se usa para
-- definir la estructura de la base de datos: CREATE, ALTER, DROP.
-- Este script es idempotente: puede ejecutarse múltiples veces sin error
-- gracias a las cláusulas "IF NOT EXISTS".
--
-- INSTRUCCIONES DE EJECUCIÓN:
-- 1. Abrir MySQL CLI o MySQL Workbench.
-- 2. Ejecutar: source C:/Projects/projecto_diseno_y_desarrollo_web/schema.sql
-- ============================================================================

-- Crear la base de datos si no existe.
-- utf8mb4 soporta emojis y caracteres especiales (á, ñ, ü, etc.)
CREATE DATABASE IF NOT EXISTS agendify
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Seleccionar la base de datos para las operaciones siguientes.
USE agendify;

-- ============================================================================
-- TABLA: eventos
-- PROPÓSITO: Almacena la información de cada evento del calendario.
--
-- CAMPOS:
--   id            → Identificador único, autoincremental (Primary Key).
--   titulo        → Nombre del evento. Obligatorio, entre 3 y 100 caracteres.
--   descripcion   → Detalle extendido del evento. Opcional.
--   fecha         → Fecha del evento (solo fecha, sin hora). Obligatorio.
--   hora          → Hora de inicio del evento. Obligatorio.
--   ubicacion     → Lugar físico o enlace virtual. Opcional.
--   capacidad     → Número máximo de asistentes. Debe ser mayor a 0.
--   tipo_evento   → Categoría del evento (ENUM restringido).
--   prioridad     → Nivel de urgencia (ENUM restringido).
--   recordatorio  → Si se debe enviar recordatorio (booleano).
--   created_at    → Fecha/hora de creación (se asigna automáticamente).
--   updated_at    → Fecha/hora de última actualización (se actualiza sola).
-- ============================================================================
CREATE TABLE IF NOT EXISTS eventos (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    titulo          VARCHAR(100)    NOT NULL,
    descripcion     TEXT            DEFAULT NULL,
    fecha           DATE            NOT NULL,
    hora            TIME            NOT NULL,
    ubicacion       VARCHAR(150)    DEFAULT NULL,
    capacidad       INT             NOT NULL DEFAULT 1,
    tipo_evento     ENUM('taller', 'reunion', 'social', 'conferencia', 'otro')
                                    NOT NULL DEFAULT 'otro',
    prioridad       ENUM('baja', 'media', 'alta')
                                    NOT NULL DEFAULT 'media',
    recordatorio    BOOLEAN         DEFAULT FALSE,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP,

    -- Restricciones de integridad a nivel de base de datos.
    -- Estas actúan como una "segunda línea de defensa" después de la
    -- validación en Python, asegurando que datos inválidos nunca se almacenen.
    CONSTRAINT chk_capacidad    CHECK (capacidad > 0),
    CONSTRAINT chk_titulo_len   CHECK (CHAR_LENGTH(titulo) >= 3)
) ENGINE=InnoDB;
