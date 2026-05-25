/**
 * ARCHIVO: static/js/main.js
 * PROPÓSITO: Gestionar la lógica de una Single Page Application (SPA) para "Agendify".
 * 
 * Se implementa la conexión con la API RESTful del backend mediante la API Fetch
 * utilizando un patrón de llamadas centralizado e interactores seguros de DOM para 
 * evitar vulnerabilidades como Cross-Site Scripting (XSS).
 * 
 * CARACTERÍSTICAS TÉCNICAS:
 *   1. Interceptor de red `apiRequest` para estandarizar llamadas y respuestas JSON.
 *   2. Sanitización contra XSS en datos dinámicos mediante función `escapeHTML`.
 *   3. Gestión de estados asíncronos y deshabilitación preventiva de botones (Race Conditions).
 *   4. Control dinámico de permisos basado en el creador del evento y roles del usuario.
 */

const app = document.getElementById('app');

// ============================================================================
// ESTADO GLOBAL DE LA APLICACIÓN (Single Source of Truth)
// ============================================================================
const appState = {
    eventos: [],           // Lista de eventos cargados para la página actual
    eventoActual: null,    // Evento en edición en el formulario
    page: 1,               // Índice de la página de eventos actual (empezando en 1)
    limit: 5,              // Límite de eventos a mostrar por página
    totalPages: 1,         // Total de páginas calculadas por el backend
    usuarioLogueado: null, // Datos del usuario autenticado actual {id, nombre, email, es_admin}
    usuariosAdmin: [],     // Colección de todos los usuarios (exclusivo Admin)
    usuarioAdminActual: null, // Usuario en edición en el panel administrativo
    filters: {             // Filtros de búsqueda avanzados activos
        fecha: '',
        tipo_evento: '',
        prioridad: '',
        creador_id: '',
        creador_texto: ''
    }
};

// ============================================================================
// UTILIDADES DE SEGURIDAD Y RED
// ============================================================================

/**
 * Sanitiza cadenas de texto para evitar vulnerabilidades de Cross-Site Scripting (XSS).
 * @param {string} str Cadena a sanitizar
 * @returns {string} Cadena segura para inyectar en HTML
 */
function escapeHTML(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Interceptor centralizado para realizar peticiones de red seguras.
 * @param {string} url Endpoint de destino
 * @param {Object} options Opciones para la petición fetch
 * @returns {Promise<any>} Datos JSON devueltos por el servidor
 */
async function apiRequest(url, options = {}) {
    const defaultHeaders = {
        'Content-Type': 'application/json'
    };

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers
        }
    };

    const response = await fetch(url, config);
    const contentType = response.headers.get('content-type');
    
    let result = null;
    if (contentType && contentType.includes('application/json')) {
        result = await response.json().catch(() => null);
    }

    if (!response.ok) {
        const errorMsg = (result && result.message) || `Error del Servidor (${response.status})`;
        const errorDetails = result && result.data;
        const err = new Error(errorMsg);
        err.status = response.status;
        err.data = errorDetails;
        throw err;
    }

    return result;
}

/**
 * Determina si el usuario logueado actual tiene privilegios para administrar un recurso.
 * @param {Object} creadorId ID del creador del recurso
 * @returns {boolean} True si posee privilegios
 */
function poseePermisosDeModificacion(creadorId) {
    if (!appState.usuarioLogueado) return false;
    return appState.usuarioLogueado.es_admin || appState.usuarioLogueado.id === creadorId;
}

// ============================================================================
// VISTAS DE LA SPA (PLANTILLAS HTML)
// ============================================================================
const views = {
    login: `
        <div class="fixed inset-0 z-0">
            <div class="absolute inset-0 bg-executive-gradient opacity-90 mix-blend-multiply"></div>
        </div>
        <main class="relative z-10 w-full min-h-screen flex items-center justify-center p-md">
            <div class="bg-surface-container-lowest rounded-xl shadow-[0px_10px_25px_-5px_rgba(10,37,64,0.08)] p-xxl flex flex-col items-center w-full max-w-[440px]">
                <div class="mb-xxl text-center">
                    <div class="flex items-center justify-center gap-sm mb-xs">
                        <span class="material-symbols-outlined text-secondary text-[32px]">event_available</span>
                        <h1 class="font-h1 text-h2 text-primary-container tracking-tight">Agendify</h1>
                    </div>
                    <p class="font-body-sm text-on-surface-variant">Gestión de Eventos Empresarial</p>
                </div>
                <!-- Banner de error para login interactivo en interfaz (Premium UX) -->
                <div id="loginError" class="hidden w-full mb-md p-sm bg-rose-50 border border-rose-100 text-rose-700 rounded-lg text-xs font-semibold leading-relaxed"></div>
                <form id="loginForm" class="w-full space-y-lg">
                    <div class="space-y-xs">
                        <label class="font-label-bold text-label-bold text-primary-container block" for="email">Usuario</label>
                        <input class="w-full px-md py-md bg-white border border-outline-variant rounded-lg font-body-sm focus:outline-none focus:ring-2 focus:ring-secondary/20 focus:border-secondary transition-all" id="email" type="text" value="admin@agendify.com" required/>
                    </div>
                    <div class="space-y-xs">
                        <label class="font-label-bold text-label-bold text-primary-container block" for="password">Contraseña</label>
                        <input class="w-full px-md py-md bg-white border border-outline-variant rounded-lg font-body-sm focus:outline-none focus:ring-2 focus:ring-secondary/20 focus:border-secondary transition-all" id="password" type="password" value="admin123" required/>
                    </div>
                    <button type="submit" id="loginSubmitBtn" class="w-full btn-primary-gradient py-md px-lg rounded-lg text-on-primary font-label-bold shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-sm">
                        <span>Ingresar al Tablero</span>
                    </button>
                </form>
            </div>
        </main>
    `,
    
    dashboard: `
        <div class="flex h-screen overflow-hidden">
            <aside class="w-64 border-r border-slate-200 bg-white shadow-sm flex flex-col py-6 px-4 shrink-0">
                <div class="flex items-center gap-3 mb-10 px-2">
                    <span class="material-symbols-outlined text-secondary text-[32px]">event_available</span>
                    <div>
                        <h1 class="text-xl font-black tracking-tight text-blue-950">Agendify</h1>
                        <p class="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Suite Ejecutiva</p>
                    </div>
                </div>
                <nav class="flex-1 space-y-1" id="sidebarNav">
                    <a class="nav-item active flex items-center gap-3 px-3 py-2.5 rounded-lg text-blue-700 font-bold border-l-4 border-blue-700 bg-slate-50" href="#" data-view="dashboard">
                        <span class="material-symbols-outlined">dashboard</span>
                        <span class="text-sm font-medium">Tablero</span>
                    </a>
                </nav>
                <div class="mt-auto pt-lg border-t border-slate-100 flex flex-col gap-md">
                    <!-- Widget de Perfil de Usuario Logueado -->
                    <div class="flex items-center gap-sm px-2 py-1.5 bg-slate-50 border border-slate-100 rounded-xl">
                        <div class="w-10 h-10 rounded-full bg-executive-gradient text-white font-bold flex items-center justify-center text-sm shrink-0 shadow-sm" id="userAvatar">
                            U
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-xs font-bold text-slate-800 truncate animate-pulse" id="userSidebarName">Cargando...</p>
                            <p class="text-[10px] text-slate-400 truncate" id="userSidebarEmail">correo@agendify.com</p>
                        </div>
                    </div>
                    <!-- Botón de Cerrar Sesión Moderno -->
                    <button class="w-full py-3 bg-primary-container text-white rounded-xl font-label-bold flex items-center justify-center gap-2 hover:opacity-90 transition-all text-sm shadow-sm" id="logoutBtn">
                        <span class="material-symbols-outlined text-sm">logout</span> Cerrar Sesión
                    </button>
                </div>
            </aside>
            <div class="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
                <header class="w-full border-b border-slate-200 bg-white/80 backdrop-blur-md flex justify-between items-center h-16 px-8 shrink-0">
                    <h2 class="font-h3 text-primary">Listado de Eventos</h2>
                    <button id="createEventBtn" class="bg-gradient-to-br from-primary-container to-secondary py-2 px-4 rounded-lg text-white font-label-bold flex items-center gap-2 hover:shadow-md transition-all">
                        <span class="material-symbols-outlined">add</span> Nuevo Evento
                    </button>
                </header>
                <main class="flex-1 p-margin-page overflow-y-auto bg-surface space-y-lg">
                    <!-- Barra de Filtros Avanzados (Premium UX) -->
                    <div class="max-w-container-max mx-auto bg-white rounded-xl shadow-sm border border-slate-200 p-md flex flex-wrap gap-md items-end">
                        <!-- Filtro por Fecha -->
                        <div class="flex-1 min-w-[150px] space-y-xs">
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block" for="filterFecha">Fecha</label>
                            <input type="date" id="filterFecha" class="w-full h-10 px-md border border-slate-200 rounded-lg text-sm focus:border-secondary outline-none transition-colors" onchange="aplicarFiltros()"/>
                        </div>
                        
                        <!-- Filtro por Tipo de Evento -->
                        <div class="flex-1 min-w-[150px] space-y-xs">
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block" for="filterTipo">Tipo de Evento</label>
                            <select id="filterTipo" class="w-full h-10 px-md border border-slate-200 bg-white rounded-lg text-sm focus:border-secondary outline-none transition-colors" onchange="aplicarFiltros()">
                                <option value="">Todos los tipos</option>
                                <option value="reunion">Reunión</option>
                                <option value="taller">Taller</option>
                                <option value="conferencia">Conferencia</option>
                                <option value="social">Social</option>
                                <option value="otro">Otro</option>
                            </select>
                        </div>
                        
                        <!-- Filtro por Prioridad -->
                        <div class="flex-1 min-w-[150px] space-y-xs">
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block" for="filterPrioridad">Prioridad</label>
                            <select id="filterPrioridad" class="w-full h-10 px-md border border-slate-200 bg-white rounded-lg text-sm focus:border-secondary outline-none transition-colors" onchange="aplicarFiltros()">
                                <option value="">Todas las prioridades</option>
                                <option value="baja">Baja</option>
                                <option value="media">Media</option>
                                <option value="alta">Alta</option>
                            </select>
                        </div>
                        
                        <!-- Filtro por Organizador (Autocomplete Interactiva con Chips estilo Google Calendar / Teams) -->
                        <div class="flex-2 min-w-[240px] space-y-xs relative">
                            <label class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block" for="filterOrganizador">Organizador</label>
                            
                            <!-- Caja del Buscador (Se muestra por defecto) -->
                            <div id="filterOrganizadorInputContainer" class="flex gap-xs items-center relative">
                                <input type="text" id="filterOrganizador" placeholder="Nombre o correo..." class="w-full h-10 px-md border border-slate-200 rounded-lg text-sm focus:border-secondary outline-none transition-colors" oninput="buscarSugerenciasOrganizadores(this.value)"/>
                            </div>
                            
                            <!-- Chip de Organizador Seleccionado (Oculto por defecto) -->
                            <div id="filterOrganizadorChipContainer" class="hidden h-10 px-sm bg-blue-50 border border-blue-100 rounded-lg flex items-center justify-between gap-sm transition-all duration-300">
                                <div class="flex items-center gap-xs min-w-0">
                                    <div class="w-6 h-6 rounded-full bg-secondary text-white font-bold flex items-center justify-center text-[10px] shrink-0" id="filterOrganizadorAvatar">
                                        U
                                    </div>
                                    <span class="text-xs font-semibold text-blue-950 truncate" id="filterOrganizadorName">Organizador</span>
                                </div>
                                <button onclick="limpiarFiltroOrganizador()" class="w-6 h-6 rounded-full hover:bg-blue-100 text-blue-500 hover:text-blue-700 transition-all font-bold text-lg flex items-center justify-center shrink-0" title="Limpiar organizador">&times;</button>
                            </div>

                            <!-- Panel de Sugerencias Flotante -->
                            <div id="organizadorSuggestions" class="hidden absolute top-full left-0 right-0 bg-white border border-slate-200 rounded-lg mt-1 shadow-lg max-h-48 overflow-y-auto z-40 transition-all">
                                <!-- Contenido inyectado dinámicamente -->
                            </div>
                        </div>
                        
                        <!-- Botón de Limpiar Filtros -->
                        <button onclick="restablecerFiltros()" class="h-10 px-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 font-label-bold rounded-lg text-sm transition-all flex items-center gap-xs shrink-0 shadow-sm">
                            <span class="material-symbols-outlined text-[18px]">restart_alt</span> Restablecer
                        </button>
                    </div>

                    <div id="eventsContainer" class="max-w-container-max mx-auto space-y-md">
                        <div class="text-center p-xl text-outline">Cargando eventos...</div>
                    </div>
                    
                    <div id="paginationControls" class="max-w-container-max mx-auto mt-lg flex justify-center gap-md items-center">
                    </div>
                </main>
            </div>
        </div>

        <!-- Modal de Previsualización de Evento (Con efecto Blur de Fondo) -->
        <div id="previewModal" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-md transition-all duration-300">
            <div class="bg-white rounded-2xl shadow-2xl border border-slate-100 w-full max-w-xl overflow-hidden flex flex-col relative">
                <!-- Header del Modal -->
                <div class="px-lg py-md border-b border-slate-100 flex items-center justify-between">
                    <span class="bg-surface-variant text-on-surface-variant px-3 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider" id="previewTipo">TIPO</span>
                    <button onclick="cerrarPrevisualizacion()" class="w-8 h-8 rounded-full flex items-center justify-center hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-all font-bold text-xl">&times;</button>
                </div>
                <!-- Contenido del Modal -->
                <div class="p-lg space-y-md overflow-y-auto max-h-[70vh]">
                    <h3 class="text-2xl font-bold text-blue-950 leading-tight" id="previewTitulo">Título Completo</h3>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-sm py-md border-y border-dashed border-slate-100 text-sm text-slate-600">
                        <p class="flex items-center gap-xs"><span class="material-symbols-outlined text-[18px] text-slate-400">calendar_today</span> <strong>Fecha:</strong> <span id="previewFecha">--</span></p>
                        <p class="flex items-center gap-xs"><span class="material-symbols-outlined text-[18px] text-slate-400">schedule</span> <strong>Hora:</strong> <span id="previewHora">--</span></p>
                        <p class="flex items-center gap-xs col-span-1 md:col-span-2"><span class="material-symbols-outlined text-[18px] text-slate-400">location_on</span> <strong>Lugar:</strong> <span id="previewUbicacion">--</span></p>
                        <p class="flex items-center gap-xs"><span class="material-symbols-outlined text-[18px] text-slate-400">group</span> <strong>Capacidad:</strong> <span id="previewCapacidad">--</span></p>
                        <p class="flex items-center gap-xs"><span class="material-symbols-outlined text-[18px] text-slate-400">priority_high</span> <strong>Prioridad:</strong> <span id="previewPrioridad" class="inline-block px-2 py-0.5 rounded-full font-bold text-[10px] uppercase">--</span></p>
                    </div>
                    
                    <div class="space-y-xs">
                        <span class="text-xs font-bold uppercase tracking-wider text-slate-400 block">Descripción</span>
                        <p class="text-slate-600 font-body-sm leading-relaxed whitespace-pre-wrap text-justify" id="previewDescripcion">Sin descripción.</p>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-sm pt-2 text-xs">
                        <div>
                            <span class="font-bold text-slate-400 uppercase tracking-wider block">Creado por</span>
                            <span id="previewCreador" class="text-slate-700 font-semibold text-sm">--</span>
                        </div>
                    </div>
                    
                    <div class="space-y-xs pt-2" id="previewInvitadosSeccion">
                        <span class="text-xs font-bold uppercase tracking-wider text-slate-400 block">Invitados</span>
                        <div id="previewInvitadosList" class="flex flex-wrap gap-xs">
                            <!-- Lista de Invitados -->
                        </div>
                    </div>
                </div>
                <!-- Footer del Modal -->
                <div id="previewModalFooter" class="bg-slate-50 px-lg py-md border-t border-slate-100 flex justify-end gap-sm">
                    <!-- Botones dinámicos de Editar/Eliminar -->
                </div>
            </div>
        </div>
    `,

    createEvent: `
        <div class="flex h-screen overflow-hidden">
            <aside class="w-64 border-r bg-slate-50 border-slate-200 p-4 shrink-0">
                <div class="flex items-center gap-3 mb-10 px-2">
                    <span class="material-symbols-outlined text-secondary text-[32px]">event_available</span>
                    <h1 class="text-lg font-extrabold text-slate-900">Agendify</h1>
                </div>
                <nav class="space-y-1">
                    <a class="nav-item flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-100 rounded-lg" href="#" data-view="dashboard">
                        <span class="material-symbols-outlined">arrow_back</span>
                        <span>Volver al Tablero</span>
                    </a>
                </nav>
            </aside>
            <main class="flex-1 flex flex-col h-full overflow-hidden">
                <header class="bg-white/80 border-b border-slate-200 flex items-center w-full px-6 h-16 shrink-0">
                    <h2 class="font-h3 text-primary" id="formTitle">Crear Nuevo Evento</h2>
                </header>
                <section class="flex-1 overflow-y-auto p-margin-page bg-surface">
                    <div class="max-w-3xl mx-auto">
                        <div id="formError" class="hidden mb-md p-md bg-error-container text-on-error-container rounded-lg font-body-sm"></div>
                        <form id="eventForm" class="bg-white rounded-xl form-shadow border border-slate-200 p-xl space-y-lg">
                            <input type="hidden" id="evento_id" name="id">
                            
                            <div class="space-y-sm">
                                <label class="font-label-bold text-primary block">Título del Evento *</label>
                                <input id="titulo" name="titulo" class="w-full h-12 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none" type="text" required minlength="3" maxlength="100"/>
                            </div>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
                                <div class="space-y-sm">
                                    <label class="font-label-bold text-primary block">Fecha *</label>
                                    <input id="fecha" name="fecha" class="w-full h-12 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none" type="date" required/>
                                </div>
                                <div class="space-y-sm">
                                    <label class="font-label-bold text-primary block">Hora *</label>
                                    <input id="hora" name="hora" class="w-full h-12 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none" type="time" required/>
                                </div>
                            </div>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
                                <div class="space-y-sm">
                                    <label class="font-label-bold text-primary block">Capacidad *</label>
                                    <input id="capacidad" name="capacidad" class="w-full h-12 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none" type="number" min="1" value="1" required/>
                                </div>
                                <div class="space-y-sm">
                                    <label class="font-label-bold text-primary block">Tipo de Evento *</label>
                                    <select id="tipo_evento" name="tipo_evento" class="w-full h-12 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none" required>
                                        <option value="reunion">Reunión</option>
                                        <option value="taller">Taller</option>
                                        <option value="conferencia">Conferencia</option>
                                        <option value="social">Social</option>
                                        <option value="otro">Otro</option>
                                    </select>
                                </div>
                            </div>

                            <div class="space-y-sm">
                                <label class="font-label-bold text-primary block">Ubicación</label>
                                <input id="ubicacion" name="ubicacion" class="w-full h-12 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none" type="text" maxlength="150"/>
                            </div>

                            <div class="space-y-sm">
                                <label class="font-label-bold text-primary block">Prioridad *</label>
                                <div class="flex gap-md">
                                    <label class="flex items-center gap-xs cursor-pointer"><input type="radio" name="prioridad" value="baja" class="w-4 h-4 text-secondary"> Baja</label>
                                    <label class="flex items-center gap-xs cursor-pointer"><input type="radio" name="prioridad" value="media" checked class="w-4 h-4 text-secondary"> Media</label>
                                    <label class="flex items-center gap-xs cursor-pointer"><input type="radio" name="prioridad" value="alta" class="w-4 h-4 text-secondary"> Alta</label>
                                </div>
                            </div>

                            <div class="space-y-sm">
                                <label class="font-label-bold text-primary block">Descripción</label>
                                <textarea id="descripcion" name="descripcion" class="w-full p-md border border-outline-variant rounded-lg focus:border-secondary outline-none" rows="3"></textarea>
                            </div>

                            <div class="space-y-sm">
                                <label class="flex items-center gap-sm cursor-pointer">
                                    <input id="recordatorio" name="recordatorio" type="checkbox" class="w-4 h-4 rounded border-outline-variant text-secondary focus:ring-secondary/30">
                                    <span class="font-label-bold text-primary block">Activar Recordatorio</span>
                                </label>
                            </div>

                            <div id="invitacionesSeccion" class="space-y-sm pt-md border-t border-outline-variant hidden">
                                <label class="font-label-bold text-primary block">Gestionar Invitados</label>
                                <div id="invitadosListForm" class="space-y-sm">
                                    <!-- Inyectado asíncronamente -->
                                </div>
                                <div class="flex gap-sm items-center mt-xs">
                                    <input id="invitarEmail" type="email" placeholder="correo.invitado@agendify.com" class="flex-1 h-10 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none text-sm"/>
                                    <button type="button" id="invitarBtn" class="h-10 px-lg bg-secondary text-white font-label-bold rounded-lg text-sm hover:opacity-90 disabled:opacity-50">Invitar</button>
                                </div>
                            </div>

                            <div class="flex items-center justify-end gap-md pt-lg border-t border-outline-variant">
                                <button type="button" id="cancelEventBtn" class="px-lg py-3 text-on-surface-variant font-label-bold hover:bg-slate-50 rounded-lg">Cancelar</button>
                                <button type="submit" id="eventFormSubmitBtn" class="px-xl h-12 bg-primary-container text-white font-label-bold rounded-lg shadow-md hover:bg-primary disabled:opacity-50">Guardar Evento</button>
                            </div>
                        </form>
                    </div>
                </section>
            </main>
        </div>
    `,

    adminUsers: `
        <div class="flex h-screen overflow-hidden">
            <aside class="w-64 border-r border-slate-200 bg-white shadow-sm flex flex-col py-6 px-4 shrink-0">
                <div class="flex items-center gap-3 mb-10 px-2">
                    <span class="material-symbols-outlined text-secondary text-[32px]">event_available</span>
                    <div>
                        <h1 class="text-xl font-black tracking-tight text-blue-950">Agendify</h1>
                        <p class="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Suite Ejecutiva</p>
                    </div>
                </div>
                <nav class="flex-1 space-y-1">
                    <a class="nav-item flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-500 hover:bg-slate-50 transition-all font-medium" href="#" data-view="dashboard">
                        <span class="material-symbols-outlined">dashboard</span>
                        <span class="text-sm">Tablero</span>
                    </a>
                    <a class="nav-item active flex items-center gap-3 px-3 py-2.5 rounded-lg text-blue-700 font-bold border-l-4 border-blue-700 bg-slate-50" href="#" data-view="adminUsers">
                        <span class="material-symbols-outlined">group</span>
                        <span class="text-sm">Administrar Usuarios</span>
                    </a>
                </nav>
                <div class="mt-auto pt-lg border-t border-slate-100 flex flex-col gap-md">
                    <!-- Widget de Perfil de Usuario Logueado -->
                    <div class="flex items-center gap-sm px-2 py-1.5 bg-slate-50 border border-slate-100 rounded-xl">
                        <div class="w-10 h-10 rounded-full bg-executive-gradient text-white font-bold flex items-center justify-center text-sm shrink-0 shadow-sm" id="userAvatar">
                            U
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-xs font-bold text-slate-800 truncate animate-pulse" id="userSidebarName">Cargando...</p>
                            <p class="text-[10px] text-slate-400 truncate" id="userSidebarEmail">correo@agendify.com</p>
                        </div>
                    </div>
                    <!-- Botón de Cerrar Sesión Moderno -->
                    <button class="w-full py-3 bg-primary-container text-white rounded-xl font-label-bold flex items-center justify-center gap-2 hover:opacity-90 transition-all text-sm shadow-sm" id="logoutBtn">
                        <span class="material-symbols-outlined text-sm">logout</span> Cerrar Sesión
                    </button>
                </div>
            </aside>
            <div class="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
                <header class="w-full border-b border-slate-200 bg-white/80 backdrop-blur-md flex justify-between items-center h-16 px-8 shrink-0">
                    <h2 class="font-h3 text-primary">Administración de Usuarios</h2>
                    <button id="createAdminUserBtn" class="bg-gradient-to-br from-primary-container to-secondary py-2 px-4 rounded-lg text-white font-label-bold flex items-center gap-2 hover:shadow-md transition-all">
                        <span class="material-symbols-outlined">person_add</span> Nuevo Usuario
                    </button>
                </header>
                <main class="flex-1 p-margin-page overflow-y-auto bg-surface">
                    <div class="max-w-container-max mx-auto bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                        <table class="min-w-full divide-y divide-slate-200">
                            <thead class="bg-slate-50">
                                <tr>
                                    <th class="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">ID</th>
                                    <th class="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Nombre</th>
                                    <th class="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Email</th>
                                    <th class="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Rol</th>
                                    <th class="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Estado</th>
                                    <th class="px-6 py-3 text-right text-xs font-bold text-slate-500 uppercase tracking-wider">Acciones</th>
                                </tr>
                            </thead>
                            <tbody id="usersTableBody" class="bg-white divide-y divide-slate-200">
                                <tr><td colspan="6" class="px-6 py-4 text-center text-slate-400">Cargando usuarios...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </main>
            </div>
        </div>

        <!-- Modal para Crear/Editar Usuario -->
        <div id="userModal" class="hidden fixed inset-0 z-50 overflow-y-auto bg-black/50 flex items-center justify-center p-md">
            <div class="bg-white rounded-xl shadow-xl border border-slate-200 w-full max-w-lg p-xl space-y-lg">
                <h3 class="text-xl font-bold text-primary" id="userModalTitle">Nuevo Usuario</h3>
                <div id="userModalError" class="hidden p-md bg-error-container text-on-error-container rounded-lg font-body-sm"></div>
                <form id="userModalForm" class="space-y-md">
                    <input type="hidden" id="user_id">
                    <div class="space-y-xs">
                        <label class="font-label-bold text-primary block" for="user_nombre">Nombre Completo *</label>
                        <input class="w-full px-md py-md border border-outline-variant rounded-lg outline-none" id="user_nombre" type="text" required minlength="3"/>
                    </div>
                    <div class="space-y-xs">
                        <label class="font-label-bold text-primary block" for="user_email">Correo Electrónico *</label>
                        <input class="w-full px-md py-md border border-outline-variant rounded-lg outline-none" id="user_email" type="email" required/>
                    </div>
                    <div class="space-y-xs">
                        <label class="font-label-bold text-primary block" id="passwordLabel" for="user_password">Contraseña *</label>
                        <input class="w-full px-md py-md border border-outline-variant rounded-lg outline-none" id="user_password" type="password"/>
                        <p class="text-xs text-slate-400" id="passwordHelp">Dejar en blanco para mantener la contraseña actual.</p>
                    </div>
                    <div class="flex gap-lg">
                        <label class="flex items-center gap-xs cursor-pointer">
                            <input id="user_es_admin" type="checkbox" class="w-4 h-4 rounded border-outline-variant text-secondary">
                            <span class="font-label-bold text-primary block">Es Administrador</span>
                        </label>
                        <label class="flex items-center gap-xs cursor-pointer">
                            <input id="user_activo" type="checkbox" class="w-4 h-4 rounded border-outline-variant text-secondary" checked>
                            <span class="font-label-bold text-primary block">Cuenta Activa</span>
                        </label>
                    </div>
                    <div class="flex items-center justify-end gap-md pt-lg border-t border-outline-variant">
                        <button type="button" id="closeUserModalBtn" class="px-lg py-3 text-on-surface-variant font-label-bold hover:bg-slate-50 rounded-lg">Cancelar</button>
                        <button type="submit" id="userModalFormSubmitBtn" class="px-xl h-12 bg-primary-container text-white font-label-bold rounded-lg shadow-md hover:bg-primary disabled:opacity-50">Guardar</button>
                    </div>
                </form>
            </div>
        </div>
    `
};

// ============================================================================
// NAVEGACIÓN Y SINCRONIZACIÓN DE LA SESIÓN DE USUARIO
// ============================================================================
async function renderView(viewName) {
    if (viewName !== 'login' && !appState.usuarioLogueado) {
        try {
            const result = await apiRequest('/api/auth/me');
            appState.usuarioLogueado = result.data;
        } catch (e) {
            appState.usuarioLogueado = null;
            appState.eventos = [];
            viewName = 'login';
        }
    }

    app.innerHTML = views[viewName];
    setupEventListeners(viewName);

    // --- POPULAR DATOS DEL USUARIO LOGUEADO EN EL SIDEBAR ---
    if (viewName !== 'login' && appState.usuarioLogueado) {
        const sideName = document.getElementById('userSidebarName');
        const sideEmail = document.getElementById('userSidebarEmail');
        const avatar = document.getElementById('userAvatar');
        
        if (sideName) {
            sideName.textContent = appState.usuarioLogueado.nombre;
            sideName.classList.remove('animate-pulse');
        }
        if (sideEmail) {
            sideEmail.textContent = appState.usuarioLogueado.email;
        }
        if (avatar) {
            const inicial = appState.usuarioLogueado.nombre ? appState.usuarioLogueado.nombre.charAt(0).toUpperCase() : 'U';
            avatar.textContent = inicial;
        }
    }

    if (viewName === 'dashboard') {
        if (appState.usuarioLogueado && appState.usuarioLogueado.es_admin) {
            const sidebarNav = document.getElementById('sidebarNav');
            if (sidebarNav && !document.getElementById('adminUsersLink')) {
                sidebarNav.innerHTML += `
                    <a class="nav-item flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-500 hover:bg-slate-50 transition-all font-medium" href="#" data-view="adminUsers" id="adminUsersLink">
                        <span class="material-symbols-outlined">group</span>
                        <span class="text-sm">Administrar Usuarios</span>
                    </a>
                `;
                setupEventListeners(viewName); // Rebind de eventos
            }
        }

        // --- SINCRONIZACIÓN DE INTERFAZ DE FILTROS ACTIVA ---
        if (appState.filters.creador_id) {
            const inputContainer = document.getElementById('filterOrganizadorInputContainer');
            const chipContainer = document.getElementById('filterOrganizadorChipContainer');
            const nameSpan = document.getElementById('filterOrganizadorName');
            const avatarDiv = document.getElementById('filterOrganizadorAvatar');
            const input = document.getElementById('filterOrganizador');
            
            if (nameSpan) nameSpan.textContent = appState.filters.creador_texto;
            if (avatarDiv) {
                avatarDiv.textContent = appState.filters.creador_texto ? appState.filters.creador_texto.charAt(0).toUpperCase() : 'U';
            }
            if (input) input.value = appState.filters.creador_texto;
            if (inputContainer) inputContainer.classList.add('hidden');
            if (chipContainer) chipContainer.classList.remove('hidden');
        }
        
        if (appState.filters.fecha) {
            const fInput = document.getElementById('filterFecha');
            if (fInput) fInput.value = appState.filters.fecha;
        }
        if (appState.filters.tipo_evento) {
            const tSelect = document.getElementById('filterTipo');
            if (tSelect) tSelect.value = appState.filters.tipo_evento;
        }
        if (appState.filters.prioridad) {
            const pSelect = document.getElementById('filterPrioridad');
            if (pSelect) pSelect.value = appState.filters.prioridad;
        }

        cargarEventos();
    } else if (viewName === 'createEvent') {
        prepararFormulario();
    } else if (viewName === 'adminUsers') {
        cargarUsuariosAdmin();
    }
}

function setupEventListeners(viewName) {
    if (viewName === 'login') {
        document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('loginSubmitBtn');
            const errorDiv = document.getElementById('loginError');
            
            if (errorDiv) errorDiv.classList.add('hidden');
            if (btn) btn.disabled = true;
 
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const result = await apiRequest('/api/auth/login', {
                    method: 'POST',
                    body: JSON.stringify({email, password})
                });
                appState.usuarioLogueado = result.data;
                renderView('dashboard');
            } catch (error) { 
                if (errorDiv) {
                    errorDiv.innerHTML = `<div class="flex items-center gap-xs"><span class="material-symbols-outlined text-[16px] mr-1">error</span><span>${escapeHTML(error.message || 'Credenciales inválidas.')}</span></div>`;
                    errorDiv.classList.remove('hidden');
                } else {
                    alert(error.message || 'Credenciales inválidas.');
                }
            } finally {
                if (btn) btn.disabled = false;
            }
        });
    } else if (viewName === 'dashboard') {
        document.getElementById('createEventBtn')?.addEventListener('click', () => {
            appState.eventoActual = null;
            renderView('createEvent');
        });
        
        document.getElementById('logoutBtn')?.addEventListener('click', async () => {
            try {
                await apiRequest('/api/auth/logout', {method: 'POST'});
            } catch (err) {
                console.warn("Fallo informando logout al backend.");
            }
            appState.usuarioLogueado = null;
            appState.eventos = [];
            renderView('login');
        });

        // Delegación de clics interactiva para las sugerencias de organizadores
        document.getElementById('organizadorSuggestions')?.addEventListener('click', (e) => {
            const item = e.target.closest('.user-suggestion-item');
            if (item) {
                const id = parseInt(item.getAttribute('data-user-id'), 10);
                const nombre = item.getAttribute('data-user-name');
                seleccionarOrganizadorFiltro(id, nombre);
            }
        });
    } else if (viewName === 'createEvent') {
        document.getElementById('cancelEventBtn')?.addEventListener('click', () => renderView('dashboard'));
        document.getElementById('eventForm')?.addEventListener('submit', handleFormSubmit);
        
        document.getElementById('invitarBtn')?.addEventListener('click', async () => {
            const btn = document.getElementById('invitarBtn');
            const emailInput = document.getElementById('invitarEmail');
            const email = emailInput.value.trim();
            const eventoId = document.getElementById('evento_id').value;
            
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert("Ingrese un correo electrónico válido.");
                return;
            }
            
            if (btn) btn.disabled = true;
            try {
                await apiRequest(`/api/eventos/${eventoId}/invitados`, {
                    method: 'POST',
                    body: JSON.stringify({ email })
                });
                emailInput.value = '';
                await cargarInvitadosForm(eventoId);
            } catch (err) {
                alert(err.message || "Error al invitar.");
            } finally {
                if (btn) btn.disabled = false;
            }
        });
    } else if (viewName === 'adminUsers') {
        document.getElementById('createAdminUserBtn')?.addEventListener('click', () => {
            appState.usuarioAdminActual = null;
            
            document.getElementById('userModalTitle').textContent = "Nuevo Usuario";
            document.getElementById('user_id').value = '';
            document.getElementById('user_nombre').value = '';
            document.getElementById('user_email').value = '';
            document.getElementById('user_password').value = '';
            
            document.getElementById('passwordLabel').textContent = "Contraseña *";
            document.getElementById('user_password').setAttribute('required', 'required');
            document.getElementById('passwordHelp').classList.add('hidden');
            
            document.getElementById('user_es_admin').checked = false;
            document.getElementById('user_activo').checked = true;
            
            document.getElementById('userModalError').classList.add('hidden');
            document.getElementById('userModal').classList.remove('hidden');
        });
        
        document.getElementById('closeUserModalBtn')?.addEventListener('click', () => {
            document.getElementById('userModal').classList.add('hidden');
        });
        
        document.getElementById('userModalForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('userModalFormSubmitBtn');
            const errorDiv = document.getElementById('userModalError');
            errorDiv.classList.add('hidden');
            if (btn) btn.disabled = true;
            
            const id = document.getElementById('user_id').value;
            const data = {
                nombre: document.getElementById('user_nombre').value,
                email: document.getElementById('user_email').value,
                es_admin: document.getElementById('user_es_admin').checked ? 1 : 0,
                activo: document.getElementById('user_activo').checked ? 1 : 0
            };
            
            const password = document.getElementById('user_password').value;
            if (password) {
                data.password = password;
            }
            
            const method = id ? 'PUT' : 'POST';
            const url = id ? `/api/admin/usuarios/${id}` : '/api/admin/usuarios';
            
            try {
                await apiRequest(url, {
                    method: method,
                    body: JSON.stringify(data)
                });
                document.getElementById('userModal').classList.add('hidden');
                await cargarUsuariosAdmin();
            } catch (err) {
                let errorMsg = err.message || "Error al guardar.";
                if (err.data && err.data.errores) {
                    errorMsg += '<br><ul class="list-disc pl-5 mt-2">' + 
                        err.data.errores.map(e => `<li>${escapeHTML(e)}</li>`).join('') + 
                        '</ul>';
                }
                errorDiv.innerHTML = errorMsg;
                errorDiv.classList.remove('hidden');
            } finally {
                if (btn) btn.disabled = false;
            }
        });
        
        document.getElementById('logoutBtn')?.addEventListener('click', async () => {
            try {
                await apiRequest('/api/auth/logout', {method: 'POST'});
            } catch (err) {
                console.warn("Fallo informando logout.");
            }
            appState.usuarioLogueado = null;
            appState.eventos = [];
            renderView('login');
        });
    }

    // Navegación local en SPA
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            const view = item.getAttribute('data-view');
            if (view) {
                e.preventDefault();
                renderView(view);
            }
        });
    });
}

// ============================================================================
// OPERACIONES CRUD DE LA API RESTful
// ============================================================================

// OBTENER Y CARGAR EVENTOS
async function cargarEventos() {
    const container = document.getElementById('eventsContainer');
    try {
        let url = `/api/eventos?page=${appState.page}&limit=${appState.limit}`;
        if (appState.filters.fecha) url += `&fecha=${encodeURIComponent(appState.filters.fecha)}`;
        if (appState.filters.tipo_evento) url += `&tipo_evento=${encodeURIComponent(appState.filters.tipo_evento)}`;
        if (appState.filters.prioridad) url += `&prioridad=${encodeURIComponent(appState.filters.prioridad)}`;
        if (appState.filters.creador_id) url += `&creador_id=${appState.filters.creador_id}`;
        
        const result = await apiRequest(url);
        const eventos = result.data.eventos;
        
        // Carga en paralelo de los invitados para cada evento (Join Client-Side seguro)
        await Promise.all(eventos.map(async (evento) => {
            try {
                const invData = await apiRequest(`/api/eventos/${evento.id}/invitados`);
                evento.invitados = invData.data;
            } catch (err) {
                evento.invitados = [];
            }
        }));

        appState.eventos = eventos;
        appState.totalPages = result.data.pagination.total_pages;
        
        renderEventsList();
        renderPagination();
    } catch (error) {
        if (error.status === 401 || error.status === 403) {
            appState.usuarioLogueado = null;
            renderView('login');
            return;
        }
        container.innerHTML = `<div class="p-xl text-error text-center font-bold">Error: ${escapeHTML(error.message)}</div>`;
    }
}

// CONTROLES DE PAGINACIÓN
function renderPagination() {
    const container = document.getElementById('paginationControls');
    if (!container) return;
    
    let html = '';
    if (appState.page > 1) {
        html += `<button onclick="cambiarPagina(${appState.page - 1})" class="px-4 py-2 border border-outline-variant rounded-lg hover:bg-surface-variant transition-all font-label-bold text-sm">Anterior</button>`;
    }
    
    html += `<span class="px-4 py-2 text-primary font-bold text-sm">Página ${appState.page} de ${appState.totalPages}</span>`;
    
    if (appState.page < appState.totalPages) {
        html += `<button onclick="cambiarPagina(${appState.page + 1})" class="px-4 py-2 border border-outline-variant rounded-lg hover:bg-surface-variant transition-all font-label-bold text-sm">Siguiente</button>`;
    }
    
    container.innerHTML = html;
}

window.cambiarPagina = (nuevaPagina) => {
    appState.page = nuevaPagina;
    cargarEventos();
};

// ============================================================================
// LÓGICA DE FILTRADO Y AUTOCOMPLETADO EN TIEMPO REAL (Filtros Avanzados)
// ============================================================================
let searchDebounceTimer = null;

window.buscarSugerenciasOrganizadores = (val) => {
    const suggBox = document.getElementById('organizadorSuggestions');
    if (!suggBox) return;
    
    clearTimeout(searchDebounceTimer);
    
    const trimmed = val.trim();
    
    // Si la entrada queda vacía, desactivamos de forma inmediata el filtro y refrescamos
    if (trimmed.length === 0) {
        appState.filters.creador_id = '';
        appState.filters.creador_texto = '';
        suggBox.innerHTML = '';
        suggBox.classList.add('hidden');
        aplicarFiltros();
        return;
    }
    
    if (trimmed.length < 2) {
        suggBox.innerHTML = '';
        suggBox.classList.add('hidden');
        return;
    }
    
    // Temporizador Debounce (mitiga peticiones excesivas en digitación rápida)
    searchDebounceTimer = setTimeout(async () => {
        try {
            const result = await apiRequest(`/api/usuarios/buscar?q=${encodeURIComponent(trimmed)}`);
            const usuarios = result.data;
            
            if (usuarios.length === 0) {
                suggBox.innerHTML = '<div class="p-2 text-xs text-slate-400 italic text-center">Sin coincidencias</div>';
                suggBox.classList.remove('hidden');
            } else {
                // Inyectamos sugerencias utilizando data-attributes (evitamos vulnerabilidades por comillas simples)
                suggBox.innerHTML = usuarios.map(u => `
                    <div data-user-id="${u.id}" data-user-name="${escapeHTML(u.nombre)}" class="user-suggestion-item p-2 text-xs hover:bg-slate-50 cursor-pointer flex flex-col gap-0.5 border-b border-slate-100 last:border-0 transition-colors">
                        <span class="font-bold text-slate-700 pointer-events-none">${escapeHTML(u.nombre)}</span>
                        <span class="text-[10px] text-slate-400 pointer-events-none">(${escapeHTML(u.email)})</span>
                    </div>
                `).join('');
                suggBox.classList.remove('hidden');
            }
        } catch (err) {
            console.error("Fallo al consultar sugerencias de usuarios en API:", err);
        }
    }, 300); // 300ms de retraso
};

window.seleccionarOrganizadorFiltro = (id, nombre) => {
    appState.filters.creador_id = id;
    appState.filters.creador_texto = nombre;
    
    const inputContainer = document.getElementById('filterOrganizadorInputContainer');
    const chipContainer = document.getElementById('filterOrganizadorChipContainer');
    const nameSpan = document.getElementById('filterOrganizadorName');
    const avatarDiv = document.getElementById('filterOrganizadorAvatar');
    const suggBox = document.getElementById('organizadorSuggestions');
    
    if (nameSpan) nameSpan.textContent = nombre;
    if (avatarDiv) {
        avatarDiv.textContent = nombre ? nombre.charAt(0).toUpperCase() : 'U';
    }
    
    if (inputContainer) inputContainer.classList.add('hidden');
    if (chipContainer) chipContainer.classList.remove('hidden');
    if (suggBox) {
        suggBox.innerHTML = '';
        suggBox.classList.add('hidden');
    }
    
    aplicarFiltros();
};

window.limpiarFiltroOrganizador = () => {
    appState.filters.creador_id = '';
    appState.filters.creador_texto = '';
    
    const inputContainer = document.getElementById('filterOrganizadorInputContainer');
    const chipContainer = document.getElementById('filterOrganizadorChipContainer');
    const input = document.getElementById('filterOrganizador');
    const suggBox = document.getElementById('organizadorSuggestions');
    
    if (input) input.value = '';
    if (inputContainer) inputContainer.classList.remove('hidden');
    if (chipContainer) chipContainer.classList.add('hidden');
    if (suggBox) {
        suggBox.innerHTML = '';
        suggBox.classList.add('hidden');
    }
    
    aplicarFiltros();
};

window.aplicarFiltros = () => {
    appState.filters.fecha = document.getElementById('filterFecha')?.value || '';
    appState.filters.tipo_evento = document.getElementById('filterTipo')?.value || '';
    appState.filters.prioridad = document.getElementById('filterPrioridad')?.value || '';
    
    appState.page = 1;
    cargarEventos();
};

window.restablecerFiltros = () => {
    appState.filters.fecha = '';
    appState.filters.tipo_evento = '';
    appState.filters.prioridad = '';
    appState.filters.creador_id = '';
    appState.filters.creador_texto = '';
    
    const inputFecha = document.getElementById('filterFecha');
    const inputTipo = document.getElementById('filterTipo');
    const inputPrioridad = document.getElementById('filterPrioridad');
    const inputOrg = document.getElementById('filterOrganizador');
    const inputContainer = document.getElementById('filterOrganizadorInputContainer');
    const chipContainer = document.getElementById('filterOrganizadorChipContainer');
    const suggBox = document.getElementById('organizadorSuggestions');
    
    if (inputFecha) inputFecha.value = '';
    if (inputTipo) inputTipo.value = '';
    if (inputPrioridad) inputPrioridad.value = '';
    if (inputOrg) inputOrg.value = '';
    
    if (inputContainer) inputContainer.classList.remove('hidden');
    if (chipContainer) chipContainer.classList.add('hidden');
    
    if (suggBox) {
        suggBox.innerHTML = '';
        suggBox.classList.add('hidden');
    }
    
    appState.page = 1;
    cargarEventos();
};

// RENDERIZAR TABLA/TARJETAS DE EVENTOS
function renderEventsList() {
    const container = document.getElementById('eventsContainer');
    if (appState.eventos.length === 0) {
        container.innerHTML = `<div class="text-center p-xl bg-white rounded-xl shadow-sm text-outline">No hay eventos registrados en este momento.</div>`;
        return;
    }

    container.innerHTML = appState.eventos.map(evento => {
        const esPropietario = appState.usuarioLogueado && appState.usuarioLogueado.id === evento.creador_id;
        const etiquetaRol = esPropietario 
            ? `<span class="bg-blue-50 text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded border border-blue-100 uppercase tracking-wider">Organizador</span>`
            : `<span class="bg-slate-50 text-slate-500 text-[10px] font-bold px-2 py-0.5 rounded border border-slate-200 uppercase tracking-wider">Invitado</span>`;

        const invitadosEscaped = (evento.invitados && evento.invitados.length > 0)
            ? evento.invitados.map(inv => `
                <span class="inline-block bg-blue-50 text-blue-700 text-[11px] font-semibold px-2 py-0.5 rounded-full border border-blue-100" title="${escapeHTML(inv.email)}">
                    ${escapeHTML(inv.nombre)}
                </span>
              `).join('')
            : '';

        return `
            <div onclick="abrirPrevisualizacion(${evento.id})" class="cursor-pointer bg-white rounded-xl p-lg border-l-4 ${getPriorityColor(evento.prioridad)} shadow-sm flex flex-col md:flex-row gap-lg justify-between items-start md:items-center hover:shadow-md hover:-translate-y-0.5 transition-all duration-300">
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-sm mb-xs flex-wrap">
                        <h3 class="font-h3 text-primary truncate max-w-[280px] md:max-w-[400px]" title="${escapeHTML(evento.titulo)}">${escapeHTML(evento.titulo)}</h3>
                        <span class="bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wider">${escapeHTML(evento.tipo_evento)}</span>
                        ${etiquetaRol}
                        <span class="text-xs text-slate-400">creado por <strong>${escapeHTML(evento.creador_nombre || 'Desconocido')}</strong></span>
                    </div>
                    <p class="font-body-sm text-on-surface-variant mb-xs flex flex-wrap items-center gap-x-md">
                        <span class="flex items-center gap-xs"><span class="material-symbols-outlined text-[16px] text-slate-400">calendar_today</span> ${escapeHTML(evento.fecha)}</span>
                        <span class="flex items-center gap-xs"><span class="material-symbols-outlined text-[16px] text-slate-400">schedule</span> ${escapeHTML(evento.hora)}</span>
                        ${evento.ubicacion ? `<span class="flex items-center gap-xs"><span class="material-symbols-outlined text-[16px] text-slate-400">location_on</span> ${escapeHTML(evento.ubicacion)}</span>` : ''}
                    </p>
                    <p class="font-body-sm text-outline mb-sm truncate max-w-[500px]">${escapeHTML(evento.descripcion) || 'Sin descripción.'}</p>
                    
                    <!-- Sección de Invitados Cruzados -->
                    ${invitadosEscaped ? `
                        <div class="mt-xs pt-xs border-t border-dashed border-slate-100 flex items-center gap-sm flex-wrap">
                            <span class="text-xs font-bold text-slate-500 flex items-center gap-xs">
                                <span class="material-symbols-outlined text-[14px]">group</span> Invitados (${evento.invitados.length}):
                            </span>
                            <div class="flex gap-xs flex-wrap">
                                ${invitadosEscaped}
                            </div>
                        </div>
                    ` : ''}
                </div>
                <div class="flex items-center gap-sm mt-md md:mt-0 shrink-0 text-slate-300 hover:text-slate-500 transition-colors">
                    <span class="text-xs text-slate-400 font-semibold hidden md:inline">Ver detalles</span>
                    <span class="material-symbols-outlined text-[24px]">chevron_right</span>
                </div>
            </div>
        `;
    }).join('');
}

function getPriorityColor(prioridad) {
    if (prioridad === 'alta') return 'border-error';
    if (prioridad === 'media') return 'border-secondary';
    return 'border-surface-tint';
}

// ABRIR MODAL DE PREVISUALIZACIÓN DE EVENTO (Con efecto Blur de Fondo)
window.abrirPrevisualizacion = (id) => {
    const evento = appState.eventos.find(e => e.id === id);
    if (!evento) return;

    // Llenar datos en el Modal
    document.getElementById('previewTipo').textContent = evento.tipo_evento;
    document.getElementById('previewTitulo').textContent = evento.titulo;
    document.getElementById('previewFecha').textContent = evento.fecha;
    document.getElementById('previewHora').textContent = evento.hora;
    document.getElementById('previewUbicacion').textContent = evento.ubicacion || 'No especificada';
    document.getElementById('previewCapacidad').textContent = `${evento.capacidad} ${evento.capacidad === 1 ? 'persona' : 'personas'}`;
    
    const prioritySpan = document.getElementById('previewPrioridad');
    prioritySpan.textContent = evento.prioridad;
    prioritySpan.className = 'inline-block px-2.5 py-0.5 rounded-full font-bold text-[10px] uppercase tracking-wider ';
    if (evento.prioridad === 'alta') {
        prioritySpan.className += 'bg-rose-50 text-rose-700 border border-rose-100';
    } else if (evento.prioridad === 'media') {
        prioritySpan.className += 'bg-indigo-50 text-indigo-700 border border-indigo-100';
    } else {
        prioritySpan.className += 'bg-slate-100 text-slate-600 border border-slate-200';
    }

    document.getElementById('previewDescripcion').textContent = evento.descripcion || 'Sin descripción detallada.';
    document.getElementById('previewCreador').textContent = evento.creador_nombre || 'Desconocido';

    // Lista de Invitados
    const invitadosList = document.getElementById('previewInvitadosList');
    const invitadosSeccion = document.getElementById('previewInvitadosSeccion');
    if (evento.invitados && evento.invitados.length > 0) {
        invitadosSeccion.classList.remove('hidden');
        invitadosList.innerHTML = evento.invitados.map(inv => `
            <span class="inline-block bg-slate-50 text-slate-600 text-[11px] font-semibold px-2.5 py-1 rounded-full border border-slate-200" title="${escapeHTML(inv.email)}">
                ${escapeHTML(inv.nombre)}
            </span>
        `).join('');
    } else {
        invitadosSeccion.classList.add('hidden');
        invitadosList.innerHTML = '';
    }

    // Botones de Acción dinámicos (Editar / Eliminar solo para propietarios o admins)
    const footer = document.getElementById('previewModalFooter');
    const puedeModificar = poseePermisosDeModificacion(evento.creador_id);
    
    if (puedeModificar) {
        footer.innerHTML = `
            <button onclick="cerrarPrevisualizacion()" class="px-lg py-2.5 text-on-surface-variant font-label-bold hover:bg-slate-100 rounded-lg text-sm transition-all">Cerrar</button>
            <button onclick="editarEventoDesdePreview(${evento.id})" class="px-lg py-2.5 border border-outline-variant rounded-lg text-primary font-label-bold hover:bg-slate-50 transition-all text-sm">Editar</button>
            <button onclick="eliminarEventoDesdePreview(${evento.id})" class="px-lg py-2.5 bg-error text-on-error rounded-lg font-label-bold hover:opacity-90 transition-all text-sm">Eliminar</button>
        `;
    } else {
        footer.innerHTML = `
            <button onclick="cerrarPrevisualizacion()" class="px-xl py-2.5 bg-primary-container text-white font-label-bold hover:opacity-90 rounded-lg text-sm transition-all">Cerrar</button>
        `;
    }

    // Mostrar el modal
    const modal = document.getElementById('previewModal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
};

// CERRAR MODAL DE PREVISUALIZACIÓN DE EVENTO
window.cerrarPrevisualizacion = () => {
    const modal = document.getElementById('previewModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
};

// LLAMADAS AUXILIARES DESDE EL PREVIEW
window.editarEventoDesdePreview = (id) => {
    cerrarPrevisualizacion();
    editarEvento(id);
};

window.eliminarEventoDesdePreview = async (id) => {
    cerrarPrevisualizacion();
    await eliminarEvento(id);
};

// PREPARAR EL FORMULARIO DE EVENTOS
async function prepararFormulario() {
    const evento = appState.eventoActual;
    const titleObj = document.getElementById('formTitle');
    const invSeccion = document.getElementById('invitacionesSeccion');
    
    if (!evento) {
        titleObj.textContent = "Crear Nuevo Evento";
        if (invSeccion) invSeccion.classList.add('hidden');
        return;
    }

    titleObj.textContent = "Editar Evento";
    document.getElementById('evento_id').value = evento.id;
    document.getElementById('titulo').value = evento.titulo;
    document.getElementById('fecha').value = evento.fecha;
    document.getElementById('hora').value = evento.hora;
    document.getElementById('ubicacion').value = evento.ubicacion;
    document.getElementById('descripcion').value = evento.descripcion;
    document.getElementById('capacidad').value = evento.capacidad;
    document.getElementById('tipo_evento').value = evento.tipo_evento;
    document.getElementById('recordatorio').checked = evento.recordatorio;
    
    const radios = document.getElementsByName('prioridad');
    for (const radio of radios) {
        if (radio.value === evento.prioridad) {
            radio.checked = true;
        }
    }

    if (invSeccion) {
        invSeccion.classList.remove('hidden');
        await cargarInvitadosForm(evento.id);
    }
}

// INVITADOS DENTRO DEL FORMULARIO DE EDICIÓN
async function cargarInvitadosForm(eventoId) {
    const container = document.getElementById('invitadosListForm');
    if (!container) return;
    
    try {
        const result = await apiRequest(`/api/eventos/${eventoId}/invitados`);
        const invitados = result.data;
        
        if (invitados.length === 0) {
            container.innerHTML = `<p class="text-xs text-slate-400 italic">No hay invitados registrados en este evento.</p>`;
        } else {
            container.innerHTML = `
                <div class="flex flex-col gap-xs">
                    ${invitados.map(inv => `
                        <div class="flex items-center justify-between bg-slate-50 px-md py-xs rounded-lg border border-slate-100">
                            <div>
                                <span class="text-sm font-semibold text-slate-700">${escapeHTML(inv.nombre)}</span>
                                <span class="text-xs text-slate-400 ml-xs">(${escapeHTML(inv.email)})</span>
                            </div>
                            <button type="button" onclick="removerInvitado(${eventoId}, ${inv.id})" class="text-error font-bold text-xs hover:underline flex items-center gap-xs">
                                <span class="material-symbols-outlined text-[14px]">close</span> Remover
                            </button>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    } catch (error) {
        console.error("Fallo al obtener la lista de invitados para el formulario:", error);
    }
}

window.mostrarConfirmacion = (titulo, mensaje, onConfirm) => {
    const modal = document.getElementById('confirmModal');
    const titleEl = document.getElementById('confirmModalTitle');
    const msgEl = document.getElementById('confirmModalMessage');
    const cancelBtn = document.getElementById('confirmModalCancelBtn');
    const confirmBtn = document.getElementById('confirmModalConfirmBtn');
    
    if (!modal || !titleEl || !msgEl || !cancelBtn || !confirmBtn) return;
    
    titleEl.textContent = titulo;
    msgEl.textContent = mensaje;
    
    modal.classList.remove('hidden');
    
    const newCancelBtn = cancelBtn.cloneNode(true);
    const newConfirmBtn = confirmBtn.cloneNode(true);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    
    newCancelBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });
    
    newConfirmBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
        onConfirm();
    });
};

window.removerInvitado = (eventoId, usuarioId) => {
    window.mostrarConfirmacion(
        '¿Remover Invitado?',
        '¿Está seguro de que desea remover a este invitado de la reunión?',
        async () => {
            try {
                await apiRequest(`/api/eventos/${eventoId}/invitados/${usuarioId}`, {
                    method: 'DELETE'
                });
                await cargarInvitadosForm(eventoId);
            } catch (err) {
                alert(err.message || "Error al remover invitado.");
            }
        }
    );
};

// ENVIAR EL FORMULARIO DE EVENTOS
async function handleFormSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById('eventFormSubmitBtn');
    const errorDiv = document.getElementById('formError');
    errorDiv.classList.add('hidden');
    
    if (btn) btn.disabled = true;

    const form = e.target;
    const formData = new FormData(form);
    
    const data = {
        titulo: formData.get('titulo'),
        fecha: formData.get('fecha'),
        hora: formData.get('hora'),
        ubicacion: formData.get('ubicacion'),
        descripcion: formData.get('descripcion'),
        capacidad: parseInt(formData.get('capacidad'), 10),
        tipo_evento: formData.get('tipo_evento'),
        prioridad: formData.get('prioridad'),
        recordatorio: formData.get('recordatorio') === 'on'
    };

    // --- VALIDACIÓN EXPLÍCITA EN JAVASCRIPT (REQUERIDO POR TAREA - TRANSFERENCIA) ---
    const erroresJS = [];
    
    // 1. Validar campos obligatorios
    if (!data.titulo || data.titulo.trim() === "") {
        erroresJS.push("El título del evento es obligatorio.");
    } else if (data.titulo.trim().length < 3) {
        erroresJS.push("El título debe tener al menos 3 caracteres.");
    } else if (data.titulo.trim().length > 100) {
        erroresJS.push("El título no puede exceder los 100 caracteres.");
    }
    
    if (!data.fecha || data.fecha.trim() === "") {
        erroresJS.push("La fecha del evento es obligatoria.");
    } else {
        const fechaIngresada = new Date(data.fecha + 'T00:00:00');
        const hoy = new Date();
        hoy.setHours(0,0,0,0);
        if (fechaIngresada < hoy) {
            erroresJS.push("La fecha del evento no puede ser en el pasado.");
        }
    }
    
    if (!data.hora || data.hora.trim() === "") {
        erroresJS.push("La hora del evento es obligatoria.");
    }
    
    // 2. Validar tipo numérico y campo obligatorio para capacidad
    const capacidadCruda = formData.get('capacidad');
    if (capacidadCruda === null || capacidadCruda === undefined || capacidadCruda.trim() === "") {
        erroresJS.push("La capacidad es obligatoria.");
    } else {
        const capacidadInt = parseInt(capacidadCruda, 10);
        if (isNaN(capacidadInt)) {
            erroresJS.push("La capacidad debe ser un valor numérico válido.");
        } else if (capacidadInt < 1) {
            erroresJS.push("La capacidad debe ser de al menos 1 persona.");
        }
    }
    
    if (!data.tipo_evento || data.tipo_evento.trim() === "") {
        erroresJS.push("El tipo de evento es obligatorio.");
    }
    
    if (!data.prioridad || data.prioridad.trim() === "") {
        erroresJS.push("La prioridad del evento es obligatoria.");
    }
    
    // Si hay fallos de validación, los mostramos e impedimos el envío
    if (erroresJS.length > 0) {
        let errorMsg = '<strong>Errores de validación en el cliente:</strong>';
        errorMsg += '<br><ul class="list-disc pl-5 mt-2">' + 
            erroresJS.map(e => `<li>${escapeHTML(e)}</li>`).join('') + 
            '</ul>';
        errorDiv.innerHTML = errorMsg;
        errorDiv.classList.remove('hidden');
        
        // Desplazamiento suave hacia la parte superior del formulario para visibilizar el error
        const section = document.querySelector('main section');
        if (section) {
            section.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        if (btn) btn.disabled = false;
        return;
    }

    const id = formData.get('id');
    const method = id ? 'PUT' : 'POST';
    const url = id ? `/api/eventos/${id}` : '/api/eventos';

    try {
        await apiRequest(url, {
            method: method,
            body: JSON.stringify(data)
        });
        renderView('dashboard');
    } catch (error) {
        let errorMsg = error.message || 'Error de comunicación.';
        if (error.data && error.data.errores) {
            errorMsg += '<br><ul class="list-disc pl-5 mt-2">' + 
                error.data.errores.map(e => `<li>${escapeHTML(e)}</li>`).join('') + 
                '</ul>';
        }
        errorDiv.innerHTML = errorMsg;
        errorDiv.classList.remove('hidden');
    } finally {
        if (btn) btn.disabled = false;
    }
}

window.editarEvento = (id) => {
    const evento = appState.eventos.find(e => e.id === id);
    if (evento) {
        appState.eventoActual = evento;
        renderView('createEvent');
    }
};

window.eliminarEvento = (id) => {
    cerrarPrevisualizacion();
    window.mostrarConfirmacion(
        '¿Eliminar Evento?',
        '¿Está seguro de que desea eliminar permanentemente este evento? Esta acción no es reversible.',
        async () => {
            try {
                await apiRequest(`/api/eventos/${id}`, {
                    method: 'DELETE'
                });
                cargarEventos();
            } catch (error) {
                alert(error.message || 'Error al eliminar el evento.');
            }
        }
    );
};

// ============================================================================
// PANEL DE ADMINISTRACIÓN DE USUARIOS (CRUD ADMIN)
// ============================================================================
async function cargarUsuariosAdmin() {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;
    
    try {
        const result = await apiRequest('/api/admin/usuarios');
        appState.usuariosAdmin = result.data;
        tbody.innerHTML = appState.usuariosAdmin.map(u => `
            <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">#${u.id}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-slate-800">${escapeHTML(u.nombre)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">${escapeHTML(u.email)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    <span class="px-2 py-1 rounded-full text-[10px] uppercase font-bold ${u.es_admin ? 'bg-indigo-50 text-indigo-700 border border-indigo-100' : 'bg-slate-100 text-slate-600 border border-slate-200'}">
                        ${u.es_admin ? 'Admin' : 'Normal'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    <span class="px-2 py-1 rounded-full text-[10px] uppercase font-bold ${u.activo ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-rose-50 text-rose-700 border border-rose-100'}">
                        ${u.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button onclick="editarUsuario(${u.id})" class="text-secondary hover:underline mr-lg font-bold">Editar</button>
                    ${u.id !== appState.usuarioLogueado?.id ? `
                        <button onclick="eliminarUsuario(${u.id})" class="text-error hover:underline font-bold">Eliminar</button>
                    ` : ''}
                </td>
            </tr>
        `).join('');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" class="px-6 py-4 text-center text-error font-bold">Error al cargar la lista de usuarios: ${escapeHTML(err.message)}</td></tr>`;
    }
}

window.editarUsuario = (id) => {
    const user = appState.usuariosAdmin.find(u => u.id === id);
    if (!user) return;
    
    appState.usuarioAdminActual = user;
    
    document.getElementById('userModalTitle').textContent = "Editar Usuario";
    document.getElementById('user_id').value = user.id;
    document.getElementById('user_nombre').value = user.nombre;
    document.getElementById('user_email').value = user.email;
    document.getElementById('user_password').value = '';
    
    document.getElementById('passwordLabel').textContent = "Contraseña";
    document.getElementById('user_password').removeAttribute('required');
    document.getElementById('passwordHelp').classList.remove('hidden');
    
    document.getElementById('user_es_admin').checked = user.es_admin;
    document.getElementById('user_activo').checked = user.activo;
    
    document.getElementById('userModalError').classList.add('hidden');
    document.getElementById('userModal').classList.remove('hidden');
};

window.eliminarUsuario = (id) => {
    window.mostrarConfirmacion(
        '¿Eliminar Usuario?',
        '¿Está seguro de que desea eliminar permanentemente este usuario?',
        async () => {
            try {
                await apiRequest(`/api/admin/usuarios/${id}`, {
                    method: 'DELETE'
                });
                await cargarUsuariosAdmin();
            } catch (err) {
                alert(err.message || "Error al eliminar usuario.");
            }
        }
    );
};

// ============================================================================
// INICIALIZACIÓN SPA
// ============================================================================
async function inicializarApp() {
    try {
        const result = await apiRequest('/api/auth/me');
        appState.usuarioLogueado = result.data;
        renderView('dashboard');
    } catch (e) {
        renderView('login');
    }
}

// Ocultar de forma interactiva el panel de sugerencias de organizador al hacer clic fuera (Premium UX estilo Google Calendar)
document.addEventListener('click', (e) => {
    const suggBox = document.getElementById('organizadorSuggestions');
    const inputOrg = document.getElementById('filterOrganizador');
    if (suggBox && !suggBox.classList.contains('hidden')) {
        if (e.target !== inputOrg && !suggBox.contains(e.target)) {
            suggBox.classList.add('hidden');
        }
    }
});

inicializarApp();
