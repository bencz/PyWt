/**
 * PyWt Framework Client-side JavaScript
 */

// Global state
let ws;
let widgets = {};
let currentPath = '';

// WebSocket connection management
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log('Received message:', message);
        
        // Processar apenas um tipo de mensagem por vez para evitar conflitos
        if (message.initialState) {
            console.log('Processing initial state');
            handleInitialState(message.initialState);
        }
        else if (message.updates) {
            console.log('Processing updates');
            handleUpdates(message.updates);
        }
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        setTimeout(connectWebSocket, 1000);  // Reconnect after 1s
    };
}

// Handle initial application state
function handleInitialState(state) {
    console.log('Received initial state:', state);
    if (state.widgets) {
        state.widgets.forEach(widget => {
            widgets[widget.id] = widget;
        });
        
        // Render the entire UI
        const rootWidget = Object.values(widgets).find(w => w.type === 'RootContainer');
        console.log('Root widget:', rootWidget);
        if (rootWidget) {
            const rootElement = renderWidget(rootWidget.id);
            console.log('Root element rendered:', rootElement);
            document.getElementById('app').appendChild(rootElement);
        } else {
            console.error('Root widget not found!');
        }
    } else {
        console.error('No widgets in initial state!');
    }
}

// Handle updates from the server
function handleUpdates(updates) {
    updates.forEach(update => {
        if (update.action === 'update') {
            if (!widgets[update.id]) {
                widgets[update.id] = {
                    id: update.id,
                    properties: {}
                };
            }
            widgets[update.id].properties[update.property] = update.value;
            updateWidget(update.id, update.property);
        } else if (update.action === 'remove') {
            const element = document.getElementById(update.id);
            if (element) {
                element.remove();
            }
            delete widgets[update.id];
        } else if (update.action === 'navigation') {
            // Handle navigation updates
            currentPath = update.path;
            if (update.title) {
                document.title = update.title;
            }
            
            // Update URL without page reload
            const url = new URL(window.location);
            url.searchParams.set('page', update.path);
            window.history.pushState({}, '', url);
            
            // Limpar container da aplicação para preparar para a nova página
            const appContainer = document.getElementById('app');
            while (appContainer.firstChild) {
                appContainer.removeChild(appContainer.firstChild);
            }
        } else if (update.action === 'add_widget') {
            // Adicionar um novo widget ao estado
            const widget = update.widget;
            const widgetId = widget.id;
            
            // Verificar se o widget já existe no DOM
            const existingElement = document.getElementById(widgetId);
            if (existingElement) {
                console.log(`Widget ${widgetId} já existe no DOM, atualizando propriedades`);
                // Atualizar as propriedades do widget existente
                widgets[widgetId] = widget;
                // Não precisamos re-renderizar, apenas atualizar as propriedades
                return;
            }
            
            // Adicionar o widget ao estado
            widgets[widgetId] = widget;
            
            // Se for o widget raiz, não precisamos renderizar novamente
            if (widget.type === 'RootContainer') {
                return;
            }
            
            // Verificar se o pai do widget existe
            const parentId = widget.properties.parent;
            if (!parentId) {
                console.error(`Widget ${widgetId} não tem pai definido`);
                return;
            }
            
            // Obter o elemento pai
            const parentElement = document.getElementById(parentId);
            if (!parentElement) {
                console.error(`Pai ${parentId} do widget ${widgetId} não encontrado no DOM`);
                return;
            }
            
            // Renderizar o widget e adicioná-lo ao pai
            const widgetElement = renderWidget(widgetId);
            if (widgetElement) {
                console.log(`Adicionando widget ${widgetId} ao pai ${parentId}`);
                parentElement.appendChild(widgetElement);
            }
        } else if (update.action === 'page_widgets') {
            // Recebemos todos os widgets de uma página de uma vez
            console.log(`Recebendo widgets da página ${update.page_path}`);
            
            // Remover todas as páginas existentes do estado
            // Isso é uma abordagem mais radical, mas garantirá que apenas a página atual seja renderizada
            const pageIds = Object.keys(widgets).filter(id => {
                const widget = widgets[id];
                return widget.type === 'HomePage' || widget.type === 'AboutPage' || 
                       widget.type === 'ContactPage' || widget.type === 'Page';
            });
            
            pageIds.forEach(id => {
                delete widgets[id];
                // Remover também os elementos do DOM se existirem
                const element = document.getElementById(id);
                if (element) {
                    element.remove();
                }
            });
            
            // Adicionar todos os widgets da nova página ao estado
            update.widgets.forEach(widget => {
                widgets[widget.id] = widget;
            });
            
            // Limpar o container da aplicação para a nova página
            const appContainer = document.getElementById('app');
            while (appContainer.firstChild) {
                appContainer.removeChild(appContainer.firstChild);
            }
            
            // Renderizar a página e seus widgets
            const rootWidget = Object.values(widgets).find(w => w.type === 'RootContainer');
            if (rootWidget) {
                const rootElement = renderWidget(rootWidget.id);
                if (rootElement) {
                    appContainer.appendChild(rootElement);
                }
            } else {
                console.error('Root widget not found!');
            }
            
            console.log(`Página ${update.page_path} renderizada com sucesso`);
        }
    });
}

// Render a widget based on its type
function renderWidget(id) {
    console.log('Rendering widget with ID:', id);
    const widget = widgets[id];
    if (!widget) {
        console.error('Widget not found:', id);
        return null;
    }
    
    const oldElement = document.getElementById(id);
    console.log('Widget type:', widget.type, 'properties:', widget.properties);
    
    let element;
    switch(widget.type) {
        case 'RootContainer':
        case 'Container':
            element = document.createElement('div');
            element.className = 'pywt-container';
            if (widget.type === 'RootContainer') {
                element.style.border = '1px solid #ccc';
                element.style.padding = '10px';
                element.style.borderRadius = '4px';
            }
            
            // Use the children array directly from the widget state
            const childrenIds = widget.children || [];
            console.log('Container ' + id + ' has ' + childrenIds.length + ' children:', childrenIds);
                
            // Render children
            childrenIds.forEach(childId => {
                if (widgets[childId]) {  // Make sure the child exists
                    const childElement = renderWidget(childId);
                    if (childElement) {
                        console.log('Appending child ' + childId + ' to parent ' + id);
                        element.appendChild(childElement);
                    }
                } else {
                    console.error('Child widget not found:', childId);
                }
            });
            break;
            
        case 'Page':
        case 'HomePage':
        case 'AboutPage':
        case 'ContactPage':
            element = document.createElement('div');
            element.className = 'pywt-page';
            
            // Verificar se a página deve estar visível
            const isVisible = widget.properties.visible === true;
            console.log(`Renderizando página ${id} (${widget.type}), visível: ${isVisible}`);
            
            if (!isVisible) {
                console.log(`Página ${id} está oculta, não renderizando seus filhos`);
                element.style.display = 'none';
                break; // Não renderizar filhos de páginas ocultas
            }
            
            // Use the children array directly from the widget state
            const pageChildrenIds = widget.children || [];
            console.log(`Página ${id} tem ${pageChildrenIds.length} filhos para renderizar`);
            
            // Render children
            pageChildrenIds.forEach(childId => {
                if (widgets[childId]) {  // Make sure the child exists
                    const childElement = renderWidget(childId);
                    if (childElement) {
                        element.appendChild(childElement);
                    }
                } else {
                    console.error('Child widget not found:', childId);
                }
            });
            break;
            
        case 'Button':
            element = document.createElement('button');
            element.className = 'pywt-button';
            element.textContent = widget.properties.text || 'Button';
            element.onclick = () => {
                sendEvent(id, 'click', {});
            };
            break;
            
        case 'TextBox':
            element = document.createElement('input');
            element.className = 'pywt-textbox';
            element.type = 'text';
            element.value = widget.properties.value || '';
            element.placeholder = widget.properties.placeholder || '';
            element.oninput = (e) => {
                sendEvent(id, 'change', { value: e.target.value });
            };
            break;
            
        case 'Label':
            element = document.createElement('div');
            element.className = 'pywt-label';
            element.textContent = widget.properties.text || '';
            console.log('Label ' + id + ' text:', widget.properties.text);
            break;
            
        case 'NavLink':
            element = document.createElement('a');
            element.className = 'pywt-nav-link';
            element.textContent = widget.properties.text || 'Link';
            element.href = '#';
            element.onclick = (e) => {
                e.preventDefault();
                sendEvent(id, 'click', { path: widget.properties.path });
            };
            break;
            
        default:
            console.error('Unknown widget type: ' + widget.type);
            return null;
    }
    
    element.id = id;
    
    if (oldElement && oldElement.parentElement) {
        oldElement.parentElement.replaceChild(element, oldElement);
    }
    
    return element;
}

// Update a widget's properties
function updateWidget(id, property) {
    const widget = widgets[id];
    const element = document.getElementById(id);
    
    if (!element || !widget) return;
    
    switch(widget.type) {
        case 'Label':
            if (property === 'text') {
                element.textContent = widget.properties.text || '';
            }
            break;
            
        case 'Button':
            if (property === 'text') {
                element.textContent = widget.properties.text || 'Button';
            }
            break;
            
        case 'TextBox':
            if (property === 'value') {
                element.value = widget.properties.value || '';
            } else if (property === 'placeholder') {
                element.placeholder = widget.properties.placeholder || '';
            }
            break;
            
        case 'NavLink':
            if (property === 'text') {
                element.textContent = widget.properties.text || 'Link';
            }
            break;
    }
}

// Send events to the server
function sendEvent(id, eventType, data) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log('Sending ' + eventType + ' event for widget ' + id, data);
        const payload = JSON.stringify({
            event: {
                id: id,
                type: eventType,
                data: data
            }
        });
        console.log('WebSocket sending:', payload);
        ws.send(payload);
    } else {
        console.error('WebSocket not connected, cannot send event');
        if (ws) {
            console.error('WebSocket state:', ws.readyState);
        }
    }
}

// Handle browser back/forward navigation
window.onpopstate = function(event) {
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page');
    if (page && page !== currentPath) {
        sendEvent('navigation', 'navigate', { path: page });
    }
};

// Initialize on window load
window.onload = () => {
    console.log('Window loaded, connecting WebSocket');
    connectWebSocket();
    // Create app container if it doesn't exist
    if (!document.getElementById('app')) {
        console.log('Creating app container');
        document.body.appendChild(document.createElement('div')).id = 'app';
    }
    
    // Check for initial page in URL
    const urlParams = new URLSearchParams(window.location.search);
    const initialPage = urlParams.get('page');
    if (initialPage) {
        // Will be handled after connection is established
        currentPath = initialPage;
    }
};
