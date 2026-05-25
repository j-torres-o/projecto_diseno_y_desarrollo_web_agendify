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

-- Eliminar tablas existentes para garantizar una inicialización limpia
DROP TABLE IF EXISTS invitaciones_evento;
DROP TABLE IF EXISTS eventos;
DROP TABLE IF EXISTS usuarios;

-- ============================================================================
-- TABLA: usuarios
-- PROPÓSITO: Almacena la información de los usuarios del sistema.
-- CAMPOS:
--   es_admin      → Flag para control de permisos de administrador (0 = no, 1 = sí).
--   activo        → Flag para permitir o bloquear el acceso de un usuario (0 = inactivo, 1 = activo).
-- ============================================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    NOT NULL UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,
    es_admin        TINYINT(1)      NOT NULL DEFAULT 0,
    activo          TINYINT(1)      NOT NULL DEFAULT 1,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- TABLA: eventos
-- PROPÓSITO: Almacena la información de cada evento del calendario.
-- CAMPOS:
--   creador_id    → Identificador del usuario creador (Foreign Key).
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
    creador_id      INT             NOT NULL,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP,

    -- Restricciones de integridad
    CONSTRAINT chk_capacidad    CHECK (capacidad > 0),
    CONSTRAINT chk_titulo_len   CHECK (CHAR_LENGTH(titulo) >= 3),
    CONSTRAINT fk_evento_creador FOREIGN KEY (creador_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- TABLA: invitaciones_evento
-- PROPÓSITO: Tabla asociativa muchos a muchos para el sistema de invitaciones.
-- ============================================================================
CREATE TABLE IF NOT EXISTS invitaciones_evento (
    evento_id       INT NOT NULL,
    usuario_id      INT NOT NULL,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (evento_id, usuario_id),
    CONSTRAINT fk_inv_evento FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE,
    CONSTRAINT fk_inv_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;
