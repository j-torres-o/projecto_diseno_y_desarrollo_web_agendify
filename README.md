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
| **Base de Datos** | MySQL |
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
Asegúrate de tener **MySQL** instalado (Service Name: `MySQL80`) y crea una base de datos para el proyecto. 
Puedes inicializar las tablas de la base de datos usando el script temporal de inicialización:
```bash
python init_db.py
```

### 5. Ejecutar la aplicación
```bash
python app.py
```
La aplicación estará disponible en `http://localhost:5000`.

## 🧪 Pruebas Automatizadas y Aseguramiento de Calidad (QA)

El proyecto cuenta con un ecosistema completo de pruebas automatizadas con **Pytest**, estructurado en tres niveles para garantizar la estabilidad del software:

1.  **Pruebas Unitarias (`tests/unit/`):** Validaciones puras de la lógica de negocio y restricciones del modelo `Evento` (títulos vacíos, fechas futuras, rangos de capacidad, prioridades), aislando la persistencia mediante mocking con `pytest-mock`.
2.  **Pruebas de Integración (`tests/integration/`):** Pruebas de integración sobre los endpoints CRUD de la API REST (`/api/eventos`) y las rutas web principales de la SPA, interactuando contra una base de datos real de pruebas aislada (`agendify_test`).
3.  **Pruebas E2E en Navegador Real:** Simulación de la interacción del usuario en el navegador real (interactuando con los campos del formulario, guardando, editando en vivo y eliminando el evento).

### Ejecutar la Suite de Pruebas
Para ejecutar la suite de pruebas automatizadas localmente, asegúrate de activar el entorno virtual y corre:
```bash
pytest -v
```

---

## 🗺️ Hoja de Ruta (Roadmap)

- [x] **Fase 1 (Contextualización)**: Diseño de la estructura visual, maquetación (HTML/CSS) y frontend base (SPA).
- [x] **Fase 2 (Profundización)**: Configuración de base de datos MySQL, POO, RESTful API con Flask (Blueprints) y lógica CRUD completa (Fetch API).
- [x] **Fase 4 (Aseguramiento de Calidad)**: Suite de pruebas unitarias, de integración de extremo a extremo (E2E) en navegador real con Pytest.
- [ ] **Fase 3 (Siguiente paso)**: Autenticación de Usuarios (Sesiones).
- [ ] **Fase 5**: Despliegue en producción.

## 🎓 Propósito Pedagógico
Este proyecto ha sido desarrollado con fines educativos, documentando cada módulo para explicar conceptos fundamentales como el protocolo HTTP, manipulación del DOM, y persistencia de datos en sistemas relacionales.

---
Desarrollado por [j-torres-o](https://github.com/j-torres-o)
