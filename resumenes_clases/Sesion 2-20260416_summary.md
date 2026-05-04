# 📚 Resumen Detallado de la Sesión: Arquitectura y Fundamentos del Desarrollo Web

**Introducción:**
Esta sesión de encuentro se centró en establecer una base teórica robusta para el desarrollo web, preparando a los participantes para la fase de programación. Se revisaron conceptos arquitectónicos fundamentales como el **Modelo Cliente-Servidor** y el **Modelo de Tres Capas**, diferenciando claramente entre los componentes visuales (**Frontend**) y la lógica de procesamiento de datos (**Backend**). Además, se establecieron las directrices académicas y los requisitos de participación en la plataforma virtual.

---

### ✨ Puntos Clave de la Sesión
*   **Diferenciación Conceptual:** Es vital distinguir entre una **Página Web** (centrada en objetos visuales, contenido estático o campañas) y un **Aplicativo** (enfocado en la **lógica**, procesos repetitivos y cálculos).
*   **Arquitectura:** El desarrollo moderno se basa en el **Modelo Cliente-Servidor**, donde el *cliente* interactúa con la interfaz visible y el *servidor* gestiona la lógica y la base de datos.
*   **Seguridad en Transmisión de Datos:** Para el envío de información crítica (como registros de usuarios), el método más seguro y recomendado es el **Método POST**, ya que oculta los datos internamente, a diferencia del método GET.
*   **Estructura Profesional:** Se enfatizó la importancia de la **responsividad** (adaptabilidad a diferentes tamaños de pantalla: celular, tablet, escritorio) y la implementación de un **Modelo de Tres Capas** (Presentación, Negocio/Lógica, Datos).
*   **Herramientas Clave:** Se utilizará una combinación de lenguajes (HTML, CSS, JavaScript, PHP) y gestores de bases de datos (MySQL/SAM) para construir el proyecto.

---

## 🌐 Fundamentos de la Plataforma y Actividades Académicas

Se realizó una revisión del estado de las actividades académicas en la plataforma virtual.

*   **Foros de Participación:** Se deben realizar aportes en dos foros clave:
    1.  **Foro de Reconocimientos:** Debe relacionar los conceptos iniciales al diseño web.
    2.  **Foro de Debate:** Participación de discusión general.
*   **Requisito de Participación:** Se requiere realizar un mínimo de **tres aportes** de manera individual en los foros mencionados.
*   **Fechas Límite:** El plazo para realizar las participaciones en ambos foros es hasta el **19 de abril**.
*   **Aclaración de Evaluación:** Se recordó que los foros son de **participación**, y no hay una actividad de entrega formal para la Unidad 1 o Unidad 2.

## 🖥️ Conceptos de Diseño Web: Web vs. Aplicativo

Se profundizó en la distinción fundamental entre dos tipos de implementaciones digitales:

*   **Página Web:** Se describe como un conjunto de **objetos visuales** (imágenes, servicios, campañas) con enfoque más publicitario.
*   **Aplicativo (Aplicación):** Se centra en la **lógica** y los **procesos repetitivos**. La clave diferencia reside en la capacidad de ejecutar cálculos, manejar inventarios o realizar procesos automáticos complejos.
*   **Diferenciación Funcional:** Aunque la página web puede tener un *login* (registro, correo, contraseña), el aplicativo se caracteriza por su profunda funcionalidad lógica (ej. manejo de inventarios).

## 🏗️ Arquitectura del Sistema: Cliente-Servidor y Modelos de Capas

Se presentó el marco teórico para construir cualquier sistema complejo:

1.  **Modelo Cliente-Servidor:**
    *   **Cliente (Frontend):** Es la parte visible, lo que el usuario interactúa desde el navegador (HTML, CSS, JavaScript).
    *   **Servidor (Backend):** Es donde se aloja la **lógica de la aplicación** (procesos, cálculos, manejo de datos).
2.  **Modelo de Tres Capas:** Para garantizar un desarrollo robusto y mantenible, se debe separar el código en tres capas:
    *   **Capa de Presentación:** Es el **Frontend** (lo visual, los colores, la estética, el *header* y el *footer*).
    *   **Capa de Negocio (Lógica):** El **Backend**. Contiene la lógica de la aplicación y los cálculos necesarios.
    *   **Capa de Datos:** La **Base de Datos** (donde se almacena información).
3.  **Estructura de Base de Datos (CRUD):**
    *   Se debe manejar un modelo de **Entidad-Relación** que organice la información en múltiples tablas (ej. `Login`, `Registro`, `Formulario`, etc.).
    *   El sistema debe soportar las operaciones fundamentales de **CRUD**: **C**rear (Insertar), **R**eader (Consultar), **U**pdate (Editar) y **D**elete (Eliminar).

## 💻 Directrices Técnicas y Buenas Prácticas de Programación

Se abordaron aspectos cruciales para la implementación técnica del proyecto:

*   **Métodos HTTP:**
    *   **GET:** Utilizado para **obtener** información (datos que se ven en la barra de búsqueda, visibles en la URL).
    *   **POST:** Utilizado para **almacenar o actualizar** información. Es el método más seguro para enviar datos sensibles, ya que oculta la información internamente.
*   **Desarrollo Frontend:**
    *   **Lenguajes:** HTML, CSS, y **JavaScript** (fundamental).
    *   **Frameworks/Librerías:** Se recomienda el uso de **frameworks** (como Bootstrap, React, Angular) para acelerar el desarrollo.
    *   **Responsividad:** Es un requisito **fundamental**. La página debe poder visualizarse y funcionar correctamente en **todos los dispositivos** (celulares, tabletas, computadores).
*   **Organización del Proyecto:**
    *   Se recomienda encarecidamente la **documentación y el comentario del código** para asegurar que el proyecto sea legible y mantenible.
    *   Las imágenes deben organizarse en carpetas independientes y nombrarse de forma descriptiva para facilitar futuras modificaciones.

## 🚀 Conclusión y Próximos Pasos

La sesión concluyó reforzando la hoja de ruta del proyecto:

1.  **Objetivo del Proyecto:** El proyecto debe ser funcionalmente conectado (**Frontend** $\leftrightarrow$ **Backend**).
2.  **Requisito de Backend:** El usuario deberá desarrollar un **Login** y un módulo de **Registro** que almacene la información en la base de datos.
3.  **Implementación Práctica:**
    *   **Repositorio:** Se puede utilizar **GitHub** como alternativa de repositorio.
    *   **Próxima Sesión:** Se iniciará la programación práctica utilizando:
        *   **Backend/Base de Datos:** **PHP** y **MySQL** (gestionado con SAM).
        *   **Conexión:** PHP se utilizará para conectar el **Frontend** (HTML/CSS/Framework) con la base de datos, enviando la información de manera segura mediante el método **POST**.
4.  **Recomendación Final:** Se insta a los participantes a empezar a planear un proyecto personal o profesional que pueda integrar tanto la capa visual (Frontend) como la lógica de procesamiento (Backend) para las próximas sesiones.