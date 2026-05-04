/**
 * ARCHIVO: main.js
 * PROPÓSITO: Gestionar la lógica de una Single Page Application (SPA) para "Agendify".
 * 
 * NOTA EDUCATIVA:
 * En una SPA, no recargamos el navegador para cambiar de página. En su lugar, 
 * usamos JavaScript para "limpiar" el contenido actual y "escribir" el nuevo 
 * dentro de un solo archivo HTML.
 */

// 1. SELECCIÓN DEL CONTENEDOR RAÍZ
// Buscamos el elemento con ID 'app' donde se "montará" toda nuestra aplicación.
// Esta es nuestra referencia constante para interactuar con la interfaz.
const app = document.getElementById('app');

// 2. EL OBJETO 'VIEWS' (Nuestras Plantillas de Pantalla)
// Aquí guardamos el HTML de cada "página" como si fueran piezas de un rompecabezas.
// Al usar acentos graves (``), podemos escribir HTML en varias líneas (Template Literals).
const views = {
    // VISTA DE INICIO DE SESIÓN (Login)
    login: `
        <div class="fixed inset-0 z-0">
            <img class="w-full h-full object-cover opacity-10 brightness-50" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBdPsSJlnoT64HnwpuAf4hxA9jm6uTKm-60NsfStS797uL4DJpNgwtpJzXyTsXmXKe8GUwSKs7sz-y85ZDlaA8VZVsDRMyAN3PlIYuYF__4-LGraPyyP2Pa8V9Zq5YTb-pgYM5L0hiJ1Q-dihpS8FZSF2iz39U0MgJxJBHm-urQZdWsw0tT20v0QBGFYbqxM_ePNso7CjtRH8FMsqJ6d3-yrNWQKKLTEsvvKEqpgLpL_vOOy1zS7AgLkTKH-DEygo_KzTTBnj_7N27N"/>
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
                        <label class="font-label-bold text-label-bold text-primary-container block" for="email">Correo Electrónico</label>
                        <div class="relative">
                            <span class="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-outline text-[20px]">mail</span>
                            <input class="w-full pl-12 pr-md py-md bg-white border border-outline-variant rounded-lg font-body-sm focus:outline-none focus:ring-2 focus:ring-secondary/20 focus:border-secondary transition-all placeholder:text-outline/50" id="email" placeholder="nombre@empresa.com" type="email"/>
                        </div>
                    </div>
                    <div class="space-y-xs">
                        <label class="font-label-bold text-label-bold text-primary-container block" for="password">Contraseña</label>
                        <div class="relative">
                            <span class="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-outline text-[20px]">lock</span>
                            <input class="w-full pl-12 pr-md py-md bg-white border border-outline-variant rounded-lg font-body-sm focus:outline-none focus:ring-2 focus:ring-secondary/20 focus:border-secondary transition-all placeholder:text-outline/50" id="password" placeholder="••••••••" type="password"/>
                        </div>
                    </div>
                    <div class="flex items-center justify-between">
                        <label class="flex items-center gap-sm cursor-pointer group">
                            <input class="w-4 h-4 rounded border-outline-variant text-secondary focus:ring-secondary/30 transition-all" type="checkbox"/>
                            <span class="font-body-sm text-on-surface-variant group-hover:text-primary-container transition-colors">Recordarme</span>
                        </label>
                        <a class="font-label-bold text-label-bold text-secondary hover:text-primary-container transition-colors" href="#">¿Olvidó su contraseña?</a>
                    </div>
                    <button type="submit" class="w-full btn-primary-gradient py-md px-lg rounded-lg text-on-primary font-label-bold shadow-md hover:shadow-lg hover:scale-[1.01] active:scale-[0.98] transition-all flex items-center justify-center gap-sm group">
                        <span>Ingresar al Tablero</span>
                        <span class="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
                    </button>
                </form>
                <div class="mt-xxl pt-lg border-t border-surface-variant w-full text-center">
                    <p class="font-body-sm text-on-surface-variant">¿No tiene una cuenta? <a class="font-label-bold text-secondary hover:underline underline-offset-4 ml-xs transition-all" href="#">Regístrese</a></p>
                </div>
            </div>
        </main>
    `,
    // PANEL DE CONTROL (Dashboard)
    dashboard: `
        <div class="flex min-h-screen">
            <aside class="h-screen w-64 border-r border-slate-200 sticky top-0 left-0 bg-white shadow-sm flex flex-col py-6 px-4">
                <div class="flex items-center gap-3 mb-10 px-2">
                    <span class="material-symbols-outlined text-secondary text-[32px]">event_available</span>
                    <div>
                        <h1 class="text-xl font-black tracking-tight text-blue-950">Agendify</h1>
                        <p class="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Suite Ejecutiva</p>
                    </div>
                </div>
                <nav class="flex-1 space-y-1">
                    <a class="nav-item active flex items-center gap-3 px-3 py-2.5 rounded-lg text-blue-700 font-bold border-l-4 border-blue-700 bg-slate-50 transition-all" href="#" data-view="dashboard">
                        <span class="material-symbols-outlined">dashboard</span>
                        <span class="text-sm font-medium">Tablero</span>
                    </a>
                    <a class="nav-item flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-500 hover:text-blue-800 hover:bg-slate-50 transition-all" href="#">
                        <span class="material-symbols-outlined">event_available</span>
                        <span class="text-sm font-medium">Mis Eventos</span>
                    </a>
                    <a class="nav-item flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-500 hover:text-blue-800 hover:bg-slate-50 transition-all" href="#">
                        <span class="material-symbols-outlined">calendar_month</span>
                        <span class="text-sm font-medium">Calendario</span>
                    </a>
                    <a class="nav-item flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-500 hover:text-blue-800 hover:bg-slate-50 transition-all" href="#">
                        <span class="material-symbols-outlined">settings</span>
                        <span class="text-sm font-medium">Configuración</span>
                    </a>
                </nav>
                <div class="mt-auto px-2">
                    <button class="w-full py-3 bg-primary-container text-white rounded-xl font-label-bold flex items-center justify-center gap-2 shadow-lg hover:opacity-90 transition-all" id="logoutBtn">
                        <span class="material-symbols-outlined text-sm">logout</span> Cerrar Sesión
                    </button>
                </div>
            </aside>
            <div class="flex-1 flex flex-col min-w-0">
                <header class="w-full sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur-md flex justify-between items-center h-16 px-8">
                    <div class="flex items-center flex-1 max-w-xl">
                        <div class="relative w-full group">
                            <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
                            <input class="w-full bg-surface-container-low border-none rounded-full py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-secondary/20 placeholder:text-slate-400" placeholder="Buscar eventos..." type="text"/>
                        </div>
                    </div>
                    <div class="flex items-center gap-6 ml-8">
                        <span class="material-symbols-outlined text-slate-500 cursor-pointer">notifications</span>
                        <div class="flex items-center gap-3 cursor-pointer group">
                            <div class="text-right hidden sm:block">
                                <p class="font-label-bold text-blue-950 leading-none">Johnatan Torres</p>
                                <p class="text-[10px] text-slate-400 font-medium">Director de Operaciones</p>
                            </div>
                            <div class="w-10 h-10 rounded-full bg-slate-200 border-2 border-white shadow-sm overflow-hidden">
                                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuC8IeMUb2tXjUTc-ghr6uE7zGpDbz8cZ8u54f6mi-rviq3dEwy4iQwk32-bDlxJO6ei1dpYMAS1rJTCZ29a_3DG0DTbBkGMfr2oqyryI08sTxQdagPhkyG05jY-TWcTkYriPVEad3eA7GfFLh6HjPcJwF3sdrFzpVH7OKVg5A6h-u90Ak2k4Af73YBpy8U_Y9HSQIzIZdlequi1JZuySYi5Yf3RSvf_ojcRe49-qkPKkaOyqiVGuNAUc9Z4pkY5f7SIozZT7ie31MAa" alt="Perfil">
                            </div>
                        </div>
                    </div>
                </header>
                <main class="flex-1 p-margin-page overflow-y-auto">
                    <div class="max-w-container-max mx-auto">
                        <div class="flex justify-between items-end mb-xxl">
                            <div>
                                <h2 class="font-h2 text-h2 text-primary mb-xs">Próximos Eventos</h2>
                                <p class="font-body-md text-body-md text-on-surface-variant">Administre su agenda ejecutiva de alta prioridad.</p>
                            </div>
                            <button id="createEventBtn" class="bg-gradient-to-br from-primary-container to-secondary py-3 px-6 rounded-lg text-white font-label-bold flex items-center gap-2 hover:shadow-xl transition-all">
                                <span class="material-symbols-outlined">event</span> Crear Nuevo Evento
                            </button>
                        </div>
                        <div class="grid grid-cols-12 gap-gutter">
                            <div class="col-span-12 lg:col-span-8 space-y-md">
                                <div class="bg-white rounded-xl p-lg border-l-4 border-secondary shadow-sm hover:shadow-md transition-shadow flex gap-lg">
                                    <div class="flex-none text-center w-16">
                                        <p class="font-label-caps text-secondary mb-1">OCT</p>
                                        <p class="text-h3 font-h3 text-primary leading-none">24</p>
                                    </div>
                                    <div class="flex-1">
                                        <div class="flex justify-between items-start mb-sm">
                                            <h3 class="font-h3 text-h3 text-primary">Revisión de Estrategia Anual</h3>
                                            <span class="bg-secondary-fixed text-on-secondary-fixed px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">Alta Prioridad</span>
                                        </div>
                                        <p class="font-body-md text-on-surface-variant mb-md">Revisión exhaustiva de los objetivos del Q4 y alineación sobre los pilares estratégicos del año fiscal 2025.</p>
                                        <div class="flex items-center justify-between">
                                            <div class="flex -space-x-2">
                                                <div class="w-8 h-8 rounded-full bg-slate-200 border-2 border-white"></div>
                                                <div class="w-8 h-8 rounded-full bg-slate-300 border-2 border-white"></div>
                                                <div class="w-8 h-8 rounded-full bg-slate-100 border-2 border-white flex items-center justify-center text-[10px] font-bold text-slate-500">+12</div>
                                            </div>
                                            <button class="text-secondary font-label-bold flex items-center gap-1 hover:underline">Ver Detalles <span class="material-symbols-outlined text-sm">arrow_forward</span></button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-span-12 lg:col-span-4 space-y-gutter">
                                <div class="bg-white rounded-xl p-lg shadow-sm">
                                    <h4 class="font-label-bold text-primary mb-md">Octubre 2024</h4>
                                    <div class="grid grid-cols-7 gap-y-2 text-center text-[10px] font-bold text-slate-400">
                                        <div>D</div><div>L</div><div>M</div><div>M</div><div>J</div><div>V</div><div>S</div>
                                    </div>
                                    <div class="grid grid-cols-7 gap-y-2 text-center mt-2">
                                        <div class="p-1 text-caption text-slate-300">20</div>
                                        <div class="p-1 text-caption text-slate-300">21</div>
                                        <div class="p-1 text-caption text-slate-300">22</div>
                                        <div class="p-1 text-caption text-slate-300">23</div>
                                        <div class="p-1 text-caption bg-secondary text-white rounded-full font-bold">24</div>
                                        <div class="p-1 text-caption">25</div>
                                        <div class="p-1 text-caption">26</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    `,
    // CREAR EVENTO (Formulario)
    createEvent: `
        <div class="flex h-screen overflow-hidden">
            <aside class="h-screen w-64 border-r hidden md:flex flex-col bg-slate-50 border-slate-200 p-4 gap-y-2">
                <div class="flex items-center gap-3 px-2 mb-xxl">
                    <span class="material-symbols-outlined text-secondary text-[32px]">event_available</span>
                    <div>
                        <h1 class="text-lg font-extrabold text-slate-900 leading-none">Agendify</h1>
                        <p class="text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">Planeación Empresarial</p>
                    </div>
                </div>
                <nav class="space-y-1">
                    <a class="nav-item flex items-center gap-3 px-4 py-3 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-all" href="#" data-view="dashboard">
                        <span class="material-symbols-outlined">dashboard</span>
                        <span>Tablero</span>
                    </a>
                    <a class="nav-item active flex items-center gap-3 px-4 py-3 bg-white text-slate-900 rounded-lg shadow-sm font-semibold border border-slate-200" href="#">
                        <span class="material-symbols-outlined">event_available</span>
                        <span>Eventos</span>
                    </a>
                </nav>
            </aside>
            <main class="flex-1 flex flex-col overflow-hidden">
                <header class="bg-white/80 backdrop-blur-md border-b border-slate-200 flex justify-between items-center w-full px-6 h-16 shrink-0">
                    <div class="flex items-center gap-4">
                        <span class="text-xl font-black tracking-tighter text-slate-900">Agendify</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <button class="p-2 text-slate-500 hover:bg-slate-50 rounded-full"><span class="material-symbols-outlined">notifications</span></button>
                        <div class="w-8 h-8 rounded-full bg-slate-200 border border-slate-200"></div>
                    </div>
                </header>
                <section class="flex-1 overflow-y-auto p-margin-page bg-surface">
                    <div class="max-w-4xl mx-auto">
                        <header class="mb-xxl">
                            <h2 class="font-h1 text-h1 text-primary">Crear Nuevo Evento</h2>
                            <p class="text-body-lg text-on-surface-variant mt-xs">Defina los detalles de su próximo compromiso profesional.</p>
                        </header>
                        <div class="bg-white rounded-xl form-shadow border border-slate-200 overflow-hidden p-xl space-y-lg">
                            <div class="space-y-sm">
                                <label class="font-label-bold text-label-bold text-primary block">Título del Evento</label>
                                <input class="w-full h-12 px-md border border-outline-variant rounded-lg font-body-md focus:border-secondary outline-none transition-all" placeholder="ej. Sesión de Planeación Estratégica" type="text"/>
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
                                <div class="space-y-sm">
                                    <label class="font-label-bold text-label-bold text-primary block">Fecha</label>
                                    <div class="relative">
                                        <span class="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-outline">calendar_today</span>
                                        <input class="w-full h-12 pl-12 pr-md border border-outline-variant rounded-lg font-body-md focus:border-secondary outline-none transition-all" type="date"/>
                                    </div>
                                </div>
                                <div class="space-y-sm">
                                    <label class="font-label-bold text-label-bold text-primary block">Hora</label>
                                    <div class="relative">
                                        <span class="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-outline">schedule</span>
                                        <input class="w-full h-12 pl-12 pr-md border border-outline-variant rounded-lg font-body-md focus:border-secondary outline-none transition-all" type="time"/>
                                    </div>
                                </div>
                            </div>
                            <div class="space-y-sm">
                                <label class="font-label-bold text-label-bold text-primary block">Ubicación</label>
                                <div class="relative">
                                    <span class="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-outline">location_on</span>
                                    <input class="w-full h-12 pl-12 px-md border border-outline-variant rounded-lg font-body-md focus:border-secondary outline-none transition-all" placeholder="Sala o Enlace de reunión" type="text"/>
                                </div>
                            </div>
                            <div class="space-y-sm">
                                <label class="font-label-bold text-label-bold text-primary block">Descripción</label>
                                <textarea class="w-full p-md border border-outline-variant rounded-lg font-body-md focus:border-secondary outline-none transition-all" rows="4" placeholder="Puntos de la agenda, detalles adicionales..."></textarea>
                            </div>
                            <div class="flex items-center justify-end gap-md pt-lg">
                                <button id="cancelEventBtn" class="px-lg py-3 text-on-surface-variant font-label-bold hover:bg-slate-50 rounded-lg transition-all">Cancelar</button>
                                <button id="saveEventBtn" class="px-xl h-12 bg-primary-container text-white font-label-bold rounded-lg shadow-md hover:bg-primary transition-all">Crear Evento</button>
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    `
};

/**
 * 3. FUNCIÓN DE RENDERIZADO (renderView)
 * Esta función es el motor que cambia lo que vemos en pantalla.
 * @param {string} viewName - El nombre de la vista que queremos cargar.
 */
function renderView(viewName) {
    // PASO A: Limpieza. Vaciamos el contenedor 'app' para eliminar la vista anterior.
    // Esto es crucial para no acumular contenido.
    app.innerHTML = views[viewName];
    
    // PASO B: Activación. Una vez que el HTML está en el DOM, debemos añadirle la lógica.
    setupEventListeners(viewName);
}

/**
 * 4. CONFIGURACIÓN DE EVENTOS (setupEventListeners)
 * El HTML inyectado es solo visual; necesitamos decirle a los botones qué hacer.
 * @param {string} viewName - Indica el contexto de la vista actual.
 */
function setupEventListeners(viewName) {
    // Si estamos en el LOGIN, configuramos el formulario.
    if (viewName === 'login') {
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                // e.preventDefault() evita que la página se recargue (comportamiento por defecto de los forms).
                e.preventDefault();
                // Navegamos al tablero.
                renderView('dashboard');
            });
        }
    } 
    // Si estamos en el TABLERO, configuramos los botones de creación y cierre de sesión.
    else if (viewName === 'dashboard') {
        const createBtn = document.getElementById('createEventBtn');
        if (createBtn) {
            createBtn.addEventListener('click', () => {
                renderView('createEvent');
            });
        }
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                renderView('login');
            });
        }
    } 
    // Si estamos CREANDO UN EVENTO, configuramos los botones de guardar y cancelar.
    else if (viewName === 'createEvent') {
        const cancelBtn = document.getElementById('cancelEventBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                renderView('dashboard');
            });
        }
        const saveBtn = document.getElementById('saveEventBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                // Aquí en el futuro enviaríamos los datos a una base de datos.
                renderView('dashboard');
            });
        }
    }

    // Lógica genérica para cualquier elemento con la clase '.nav-item'.
    // Esto nos permite tener menús laterales que funcionen en cualquier pantalla.
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

// 5. INICIALIZACIÓN
// Al cargar el script por primera vez, mostramos la pantalla de login.
renderView('login');
