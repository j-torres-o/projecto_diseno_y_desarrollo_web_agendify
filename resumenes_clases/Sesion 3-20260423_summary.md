# 💻 Desarrollo Web: Estructura y Estilizado de Proyectos con HTML y CSS

---

### 📜 Introducción
Esta sesión marca el inicio formal del proceso de programación del proyecto en curso. El objetivo principal fue capacitar a los participantes en el uso del entorno de desarrollo **Visual Studio Code** y sentar las bases del código utilizando **HTML** para la estructura y **CSS** para el estilizado. Se profundizó en las mejores prácticas de codificación, la jerarquía de etiquetas, la implementación de elementos de navegación y la aplicación de propiedades de estilo avanzadas.

### ✨ Puntos Clave
*   **Separación de Preocupaciones:** Es fundamental entender que **HTML** se dedica exclusivamente a la **estructura** del contenido, mientras que **CSS** se encarga del **estilo** (colores, tamaños, posicionamiento, etc.).
*   **Herramienta de Desarrollo:** Se utiliza **Visual Studio Code** (`VS Code`) como entorno principal de trabajo.
*   **Estructura de Contenido:** Se deben utilizar etiquetas semánticas como `<header>`, `<section>`, y `<div>` para organizar el contenido de manera lógica.
*   **Atributos Esenciales:** Se hizo énfasis en el uso del atributo `alt` en la etiqueta `<img>` para mejorar la accesibilidad y el atributo `href` en la etiqueta `<a>` para crear hipervínculos.
*   **Manejo de Estilos:** Los estilos se deben aplicar preferentemente en un archivo externo (`.css`) y no directamente en el HTML.
*   **Próxima Etapa:** El siguiente tema a abordar será el **Diseño Responsivo** y el uso de *frameworks* como **Bootstrap**.

### ⚙️ Desarrollo Detallado

#### 1. Configuración del Entorno y Estructura HTML
*   **Workspace:** Se debe crear una carpeta predeterminada en el equipo y abrirla en **Visual Studio Code** (`Open Folder`).
*   **Archivo Principal:** Se inicia el trabajo en el archivo `index.html`.
*   **Estructura Básica:** Se revisó la estructura canónica: `<!DOCTYPE html>`, `<html>`, `<head>` (contiene metadatos, incluyendo el `<title>` para la pestaña del navegador) y `<body>` (el cuerpo visible de la página).
*   **Etiquetas Semánticas:** Se introdujeron etiquetas clave para organizar el contenido:
    *   `<header>`: Para el encabezado principal de la página.
    *   `<h1>` a `<h6>`: Etiquetas para títulos. Se debe recordar que la jerarquía va de `<h1>` (más grande y principal) a `<h6>` (más pequeño).
    *   `<p>`: Para párrafos de texto.
    *   `<nav>`: Para contener los elementos de navegación (menú).
    *   `<a>`: La etiqueta de ancla, utilizada para crear hipervínculos (`<a href="ruta.html">Texto</a>`).
    *   `<section>`: Un contenedor semántico para un área temática específica de la página.
    *   `<div>`: Un contenedor genérico, útil para agrupar elementos sin un significado semántico específico.

#### 2. La Importancia de las Clases (`class`) y las IDs (`id`)
*   **Clases vs. Secciones:** Una **Sección** es un espacio predeterminado o un alojamiento amplio. Una **Clase** es un nombre específico utilizado para aplicar estilos o seleccionar un conjunto de elementos de forma modular.
*   **Mecanismo de Estilizado:** Para aplicar estilos específicos, se debe usar el nombre de la clase o ID en el CSS (ej: `class="..."` en HTML).
*   **Selectores CSS:**
    *   Para seleccionar por clase: Se utiliza el punto (`.`) (Ejemplo: `.nombre-clase`).
    *   Para seleccionar por ID: Se utiliza el símbolo de almohadilla (`#`) (Ejemplo: `#id-nombre`).

#### 3. Manejo de Contenido Multimedia y Interacción
*   **Imágenes:** Se utiliza la etiqueta `<img>`.
    *   `src`: Indica la **ruta** (path) de la imagen (puede ser local o un *link*).
    *   `alt`: Proporciona un **texto alternativo** que se muestra en caso de error de carga o para lectores de pantalla.
*   **CSS y Estilos:**
    *   **Método Recomendado:** Conectar un archivo externo (`styles.css`).
    *   **Propiedades Clave:**
        *   `font-family`: Define el tipo de letra (Ej: `font-family: Arial;`).
        *   `background-color`: Cambia el color de fondo.
        *   `text-align`: Alinea el texto (izquierda, derecha, centro).
        *   `padding`: Define el **espacio interno** entre el contenido y el borde del elemento (Ejemplo: `padding: 20px;`).
        *   `margin`: Define el **espacio externo** entre un elemento y otros elementos colindantes.

#### 4. Buenas Prácticas y Optimización del Código
*   **Comentarios:** Es vital incluir comentarios (`<!-- comentario -->`) en el código para documentar la intención y el funcionamiento de bloques de código, facilitando la lectura y el mantenimiento por parte de otros desarrolladores.
*   **Estructuración Profesional:** Se recomienda planificar la estructura de la página utilizando una **paleta de colores** coherente y profesional para todo el proyecto.

### 🚀 Conclusión y Próximos Pasos
Se ha establecido una base sólida en la estructura y el estilizado inicial del proyecto, cubriendo desde la sintaxis básica de **HTML** hasta la aplicación de propiedades avanzadas de **CSS**.

**Indicaciones para el desarrollo:**
1.  Se debe avanzar trabajando en la conexión y modificación constante del archivo CSS.
2.  Se debe aplicar la estructura de la página de manera profesional, cuidando la alineación y los espaciados.

**Temas a cubrir en sesiones futuras:**
1.  **Diseño Responsivo:** Adaptar la página para que se vea correctamente en diferentes tamaños de pantalla (celulares, tablets, portátiles, televisores).
2.  **Frameworks:** Implementación de herramientas adicionales como **Bootstrap** para acelerar el desarrollo y asegurar el *responsive*.

**Próxima Sesión:**
*   La próxima sesión se llevará a cabo el **miércoles de la próxima semana**, con el objetivo de avanzar más rápidamente en la implementación del diseño.