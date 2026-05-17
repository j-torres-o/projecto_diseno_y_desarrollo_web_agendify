/**
 * ARCHIVO: main.js
 * PROPÓSITO: Gestionar la lógica de una Single Page Application (SPA) para "Agendify".
 * 
 * Se implementa la conexión con la API RESTful del backend mediante la API Fetch.
 */

const app = document.getElementById('app');

// Estado global de la aplicación
const appState = {
    eventos: [],
    eventoActual: null // Para edición
};

// ============================================================================
// 1. PLANTILLAS DE VISTAS (VIEWS)
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
                <form id="loginForm" class="w-full space-y-lg">
                    <div class="space-y-xs">
                        <label class="font-label-bold text-label-bold text-primary-container block" for="email">Usuario</label>
                        <input class="w-full px-md py-md bg-white border border-outline-variant rounded-lg font-body-sm focus:outline-none focus:ring-2 focus:ring-secondary/20 focus:border-secondary transition-all" id="email" type="text" value="admin" required/>
                    </div>
                    <div class="space-y-xs">
                        <label class="font-label-bold text-label-bold text-primary-container block" for="password">Contraseña</label>
                        <input class="w-full px-md py-md bg-white border border-outline-variant rounded-lg font-body-sm focus:outline-none focus:ring-2 focus:ring-secondary/20 focus:border-secondary transition-all" id="password" type="password" value="admin" required/>
                    </div>
                    <button type="submit" class="w-full btn-primary-gradient py-md px-lg rounded-lg text-on-primary font-label-bold shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-sm">
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
                <nav class="flex-1 space-y-1">
                    <a class="nav-item active flex items-center gap-3 px-3 py-2.5 rounded-lg text-blue-700 font-bold border-l-4 border-blue-700 bg-slate-50" href="#" data-view="dashboard">
                        <span class="material-symbols-outlined">dashboard</span>
                        <span class="text-sm font-medium">Tablero</span>
                    </a>
                </nav>
                <div class="mt-auto px-2">
                    <button class="w-full py-3 bg-primary-container text-white rounded-xl font-label-bold flex items-center justify-center gap-2 hover:opacity-90" id="logoutBtn">
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
                <main class="flex-1 p-margin-page overflow-y-auto bg-surface">
                    <div id="eventsContainer" class="max-w-container-max mx-auto space-y-md">
                        <!-- Los eventos se cargarán aquí dinámicamente -->
                        <div class="text-center p-xl text-outline">Cargando eventos...</div>
                    </div>
                </main>
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
                            
                            <!-- 1. Título (Text) -->
                            <div class="space-y-sm">
                                <label class="font-label-bold text-primary block">Título del Evento *</label>
                                <input id="titulo" name="titulo" class="w-full h-12 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none" type="text" required minlength="3" maxlength="100"/>
                            </div>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
                                <!-- 2. Fecha (Date) -->
                                <div class="space-y-sm">
                                    <label class="font-label-bold text-primary block">Fecha *</label>
                                    <input id="fecha" name="fecha" class="w-full h-12 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none" type="date" required/>
                                </div>
                                <!-- 3. Hora (Time) -->
                                <div class="space-y-sm">
                                    <label class="font-label-bold text-primary block">Hora *</label>
                                    <input id="hora" name="hora" class="w-full h-12 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none" type="time" required/>
                                </div>
                            </div>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
                                <!-- 4. Capacidad (Number) -->
                                <div class="space-y-sm">
                                    <label class="font-label-bold text-primary block">Capacidad *</label>
                                    <input id="capacidad" name="capacidad" class="w-full h-12 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none" type="number" min="1" value="1" required/>
                                </div>
                                <!-- 5. Tipo de Evento (Select) -->
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

                            <!-- 6. Ubicación (Text) -->
                            <div class="space-y-sm">
                                <label class="font-label-bold text-primary block">Ubicación</label>
                                <input id="ubicacion" name="ubicacion" class="w-full h-12 px-md border border-outline-variant rounded-lg focus:border-secondary outline-none" type="text" maxlength="150"/>
                            </div>

                            <!-- 7. Prioridad (Radio) -->
                            <div class="space-y-sm">
                                <label class="font-label-bold text-primary block">Prioridad *</label>
                                <div class="flex gap-md">
                                    <label class="flex items-center gap-xs"><input type="radio" name="prioridad" value="baja"> Baja</label>
                                    <label class="flex items-center gap-xs"><input type="radio" name="prioridad" value="media" checked> Media</label>
                                    <label class="flex items-center gap-xs"><input type="radio" name="prioridad" value="alta"> Alta</label>
                                </div>
                            </div>

                            <!-- 8. Descripción (Textarea) -->
                            <div class="space-y-sm">
                                <label class="font-label-bold text-primary block">Descripción</label>
                                <textarea id="descripcion" name="descripcion" class="w-full p-md border border-outline-variant rounded-lg focus:border-secondary outline-none" rows="3"></textarea>
                            </div>

                            <!-- 9. Recordatorio (Checkbox) -->
                            <div class="space-y-sm">
                                <label class="flex items-center gap-sm cursor-pointer">
                                    <input id="recordatorio" name="recordatorio" type="checkbox" class="w-4 h-4 rounded border-outline-variant text-secondary focus:ring-secondary/30">
                                    <span class="font-label-bold text-primary block">Activar Recordatorio</span>
                                </label>
                            </div>

                            <!-- 10. Botones (Submit) -->
                            <div class="flex items-center justify-end gap-md pt-lg border-t border-outline-variant">
                                <button type="button" id="cancelEventBtn" class="px-lg py-3 text-on-surface-variant font-label-bold hover:bg-slate-50 rounded-lg">Cancelar</button>
                                <button type="submit" class="px-xl h-12 bg-primary-container text-white font-label-bold rounded-lg shadow-md hover:bg-primary">Guardar Evento</button>
                            </div>
                        </form>
                    </div>
                </section>
            </main>
        </div>
    `
};

// ============================================================================
// 2. LÓGICA DE NAVEGACIÓN
// ============================================================================
function renderView(viewName) {
    app.innerHTML = views[viewName];
    setupEventListeners(viewName);

    if (viewName === 'dashboard') {
        cargarEventos();
    } else if (viewName === 'createEvent') {
        prepararFormulario();
    }
}

function setupEventListeners(viewName) {
    if (viewName === 'login') {
        document.getElementById('loginForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            renderView('dashboard');
        });
    } else if (viewName === 'dashboard') {
        document.getElementById('createEventBtn')?.addEventListener('click', () => {
            appState.eventoActual = null; // Modo creación
            renderView('createEvent');
        });
        document.getElementById('logoutBtn')?.addEventListener('click', () => renderView('login'));
    } else if (viewName === 'createEvent') {
        document.getElementById('cancelEventBtn')?.addEventListener('click', () => renderView('dashboard'));
        document.getElementById('eventForm')?.addEventListener('submit', handleFormSubmit);
    }

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
// 3. INTEGRACIÓN CON LA API RESTful (Fetch API)
// ============================================================================

// CARGAR EVENTOS (GET)
async function cargarEventos() {
    const container = document.getElementById('eventsContainer');
    try {
        const response = await fetch('/api/eventos');
        const result = await response.json();

        if (response.ok) {
            appState.eventos = result.data;
            renderEventsList();
        } else {
            container.innerHTML = `<div class="p-xl text-error text-center font-bold">Error: ${result.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="p-xl text-error text-center font-bold">Error de conexión al servidor.</div>`;
    }
}

// RENDERIZAR LISTA
function renderEventsList() {
    const container = document.getElementById('eventsContainer');
    if (appState.eventos.length === 0) {
        container.innerHTML = `<div class="text-center p-xl bg-white rounded-xl shadow-sm text-outline">No hay eventos registrados.</div>`;
        return;
    }

    container.innerHTML = appState.eventos.map(evento => `
        <div class="bg-white rounded-xl p-lg border-l-4 ${getPriorityColor(evento.prioridad)} shadow-sm flex flex-col md:flex-row gap-lg justify-between items-start md:items-center">
            <div>
                <div class="flex items-center gap-sm mb-xs">
                    <h3 class="font-h3 text-primary">${evento.titulo}</h3>
                    <span class="bg-surface-variant text-on-surface-variant px-2 py-1 rounded-full text-[10px] uppercase">${evento.tipo_evento}</span>
                </div>
                <p class="font-body-sm text-on-surface-variant mb-xs">
                    <span class="material-symbols-outlined text-[16px] align-middle">calendar_today</span> ${evento.fecha}
                    <span class="material-symbols-outlined text-[16px] align-middle ml-sm">schedule</span> ${evento.hora}
                    ${evento.ubicacion ? `<span class="material-symbols-outlined text-[16px] align-middle ml-sm">location_on</span> ${evento.ubicacion}` : ''}
                </p>
                <p class="font-body-sm text-outline">Capacidad: ${evento.capacidad} | Recordatorio: ${evento.recordatorio ? 'Sí' : 'No'}</p>
            </div>
            <div class="flex gap-sm w-full md:w-auto mt-md md:mt-0">
                <button onclick="editarEvento(${evento.id})" class="flex-1 md:flex-none px-4 py-2 border border-outline-variant rounded-lg text-primary font-label-bold hover:bg-surface-variant transition-all">Editar</button>
                <button onclick="eliminarEvento(${evento.id})" class="flex-1 md:flex-none px-4 py-2 border border-error text-error rounded-lg font-label-bold hover:bg-error-container transition-all">Eliminar</button>
            </div>
        </div>
    `).join('');
}

function getPriorityColor(prioridad) {
    if (prioridad === 'alta') return 'border-error';
    if (prioridad === 'media') return 'border-secondary';
    return 'border-surface-tint';
}

// PREPARAR FORMULARIO (Creación o Edición)
function prepararFormulario() {
    const evento = appState.eventoActual;
    const titleObj = document.getElementById('formTitle');
    if (!evento) {
        titleObj.textContent = "Crear Nuevo Evento";
        return; // Es nuevo, los defaults en HTML son suficientes
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
    
    // Seleccionar radio button correcto
    const radios = document.getElementsByName('prioridad');
    for (const radio of radios) {
        if (radio.value === evento.prioridad) {
            radio.checked = true;
        }
    }
}

// GUARDAR EVENTO (POST o PUT)
async function handleFormSubmit(e) {
    e.preventDefault();
    const errorDiv = document.getElementById('formError');
    errorDiv.classList.add('hidden');

    const form = e.target;
    const formData = new FormData(form);
    
    // Construir payload
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

    const id = formData.get('id');
    const method = id ? 'PUT' : 'POST';
    const url = id ? `/api/eventos/${id}` : '/api/eventos';

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            renderView('dashboard');
        } else {
            // Mostrar errores del backend
            let errorMsg = result.message;
            if (result.data && result.data.errores) {
                errorMsg += '<br><ul class="list-disc pl-5 mt-2">' + 
                    result.data.errores.map(err => `<li>${err}</li>`).join('') + 
                    '</ul>';
            }
            errorDiv.innerHTML = errorMsg;
            errorDiv.classList.remove('hidden');
        }
    } catch (error) {
        errorDiv.textContent = 'Error de conexión al enviar los datos.';
        errorDiv.classList.remove('hidden');
    }
}

// EDITAR EVENTO (Preparar estado)
window.editarEvento = (id) => {
    const evento = appState.eventos.find(e => e.id === id);
    if (evento) {
        appState.eventoActual = evento;
        renderView('createEvent');
    }
};

// ELIMINAR EVENTO (DELETE)
window.eliminarEvento = async (id) => {
    if (!confirm('¿Está seguro de eliminar este evento? Esta acción no se puede deshacer.')) return;

    try {
        const response = await fetch(`/api/eventos/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            cargarEventos();
        } else {
            const result = await response.json();
            alert('Error al eliminar: ' + result.message);
        }
    } catch (error) {
        alert('Error de conexión al eliminar el evento.');
    }
};

// Inicialización
renderView('login');
