# 🗓️ Agendify - Sistema de Gestión de Calendario

Bienvenido a **Agendify**, una aplicación web completa diseñada como recurso pedagógico para aprender el desarrollo de aplicaciones full-stack. Este proyecto implementa un sistema de gestión de eventos utilizando una arquitectura moderna de 3 capas.

## 🚀 Características

- **Gestión de Eventos (CRUD)**: Capacidad para Crear, Leer, Actualizar y Eliminar eventos.
- **Autenticación de Usuarios**: Registro e inicio de sesión seguro.
- **Diseño Responsivo**: Interfaz moderna adaptable a dispositivos móviles y escritorio utilizando CSS Grid y Flexbox.
- **Arquitectura Profesional**: Separación clara entre Presentación (Frontend), Lógica (Backend) y Datos (Base de Datos).

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Vanilla), JavaScript |
| **Backend** | Python, Flask |
| **Base de Datos** | PostgreSQL |
| **Arquitectura** | Modelo de 3 Capas (Presentación, Lógica, Datos) |

## ⚙️ Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto localmente:

### 1. Clonar el repositorio
```bash
git clone https://github.com/j-torres-o/projecto_diseno_y_desarrollo_web_agendify.git
cd projecto_diseno_y_desarrollo_web_agendify
```

### 2. Configurar el entorno virtual
```bash
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos
Asegúrate de tener **PostgreSQL** instalado y crea una base de datos para el proyecto. (Próximamente: Script de inicialización de tablas).

### 5. Ejecutar la aplicación
```bash
python app.py
```
La aplicación estará disponible en `http://localhost:5000`.

## 🗺️ Hoja de Ruta (Roadmap)

- [x] **Fase 1**: Diseño de la estructura visual y maquetación.
- [ ] **Fase 2**: Configuración de base de datos y conexión Flask.
- [ ] **Fase 3**: Implementación de lógica CRUD y Autenticación.
- [ ] **Fase 4**: Pulido visual y despliegue.

## 🎓 Propósito Pedagógico
Este proyecto ha sido desarrollado con fines educativos, documentando cada módulo para explicar conceptos fundamentales como el protocolo HTTP, manipulación del DOM, y persistencia de datos en sistemas relacionales.

---
Desarrollado por [j-torres-o](https://github.com/j-torres-o)
