"""
Application class for PyWt framework
"""
import asyncio
import json
from typing import Dict, List, Any, Optional, Set
from .widget import Widget


class RootContainer(Widget):
    """Root container widget that serves as the entry point for the UI"""
    def __init__(self, app):
        super().__init__()
        self.app = app
        app.register_widget(self)
        self.set_property("type", "RootContainer")
        
    def render_html(self) -> str:
        """Render the root container and all its children to HTML"""
        html = '<div id="root" class="pywt-container">'
        for child in self.children:
            html += child.render_html()
        html += '</div>'
        return html


class Application:
    """Main application class for PyWt"""
    def __init__(self):
        # Initialize dictionaries and collections first
        self.widgets: Dict[str, Widget] = {}
        self._clients = set()
        self._update_queue: List[Dict[str, Any]] = []
        self._update_task = None
        
        # Now create the root container
        self.root = RootContainer(self)
        
    def register_widget(self, widget: Widget) -> None:
        """Register a widget with the application"""
        self.widgets[widget.id] = widget
        
    def _schedule_update(self, update: Dict[str, Any]) -> None:
        """Schedule an update to be sent to clients"""
        self._update_queue.append(update)
        
        # Iniciar a tarefa de processamento apenas se necessário
        if not self._update_task or self._update_task.done():
            self._update_task = asyncio.create_task(self._process_updates())
            
    async def _process_updates(self) -> None:
        """Process and send accumulated updates to clients usando debouncing"""
        # Esperamos por mais atualizações usando uma abordagem de debounce baseada em eventos
        try:
            # Criamos uma nova future que será resolvida no próximo ciclo do event loop
            await asyncio.sleep(0)
            
            # Se não há atualizações ou clientes, não fazemos nada
            if not self._update_queue or not self._clients:
                return
                
            # Copiamos as atualizações acumuladas e limpamos a fila
            updates = self._update_queue.copy()
            self._update_queue.clear()
            
            # Enviamos as atualizações para todos os clientes
            await asyncio.gather(*(client.send_str(json.dumps({"updates": updates})) 
                                   for client in self._clients))
        except Exception as e:
            print(f"Erro ao processar atualizações: {e}")
            import traceback
            traceback.print_exc()
        
    async def connect_client(self, websocket) -> None:
        """Connect a new client websocket"""
        self._clients.add(websocket)
        
        # Send initial state to the new client
        initial_state = self._get_initial_state()
        # Use send_str for WebSocketResponse
        await websocket.send_str(json.dumps({"initialState": initial_state}))
        
    def disconnect_client(self, websocket) -> None:
        """Disconnect a client websocket"""
        if websocket in self._clients:
            self._clients.remove(websocket)
            
    def _get_initial_state(self) -> Dict[str, Any]:
        """Get the initial state of the entire application"""
        widgets_state = self._collect_widget_states(self.root)
        print(f"Sending initial state with {len(widgets_state)} widgets")
        
        # Log detailed information about each widget
        for widget_state in widgets_state:
            print(f"Widget: id={widget_state['id']}, type={widget_state.get('type', '?')}, "
                  f"parent={widget_state.get('properties', {}).get('parent', 'None')}")
            
        return {
            "widgets": widgets_state
        }
        
    def _collect_widget_states(self, widget: Widget) -> List[Dict[str, Any]]:
        """Recursively collect the states of a widget and its children"""
        states = [widget.get_initial_state()]
        
        for child in widget.children:
            states.extend(self._collect_widget_states(child))
            
        return states
        
    async def handle_client_message(self, message: Dict[str, Any]) -> None:
        """Handle a message from a client"""
        if "event" in message:
            event_data = message["event"]
            widget_id = event_data.get("id")
            event_type = event_data.get("type")
            event_value = event_data.get("data", {})
            
            print(f"Received event: {event_type} for widget {widget_id} with data {event_value}")
            
            if widget_id in self.widgets:
                widget = self.widgets[widget_id]
                print(f"Processing {event_type} on {widget.__class__.__name__}")
                try:
                    await widget.handle_event(event_type, event_value)
                except Exception as e:
                    print(f"Error handling event: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"Widget not found: {widget_id}")
                print(f"Available widgets: {list(self.widgets.keys())}")
        else:
            print(f"Received non-event message: {message}")

                
    def get_html(self) -> str:
        """Get the HTML representation of the application"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>PyWt Application</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                }}
                .pywt-container {{
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }}
                .pywt-button {{
                    padding: 8px 16px;
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    cursor: pointer;
                    border-radius: 4px;
                }}
                .pywt-button:hover {{
                    background-color: #45a049;
                }}
                .pywt-textbox {{
                    padding: 8px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }}
                .pywt-label {{
                    font-size: 16px;
                }}
            </style>
            <script>
                let ws;
                let widgets = {{}};
                
                function connectWebSocket() {{
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = `${{protocol}}//${{window.location.host}}/ws`;
                    
                    ws = new WebSocket(wsUrl);
                    
                    ws.onopen = () => {{
                        console.log('WebSocket connected');
                    }};
                    
                    ws.onmessage = (event) => {{
                        const message = JSON.parse(event.data);
                        
                        if (message.initialState) {{
                            handleInitialState(message.initialState);
                        }}
                        
                        if (message.updates) {{
                            handleUpdates(message.updates);
                        }}
                    }};
                    
                    ws.onclose = () => {{
                        console.log('WebSocket disconnected');
                        setTimeout(connectWebSocket, 1000);  // Reconnect after 1s
                    }};
                }}
                
                function handleInitialState(state) {{
                    console.log('Received initial state:', state);
                    if (state.widgets) {{
                        state.widgets.forEach(widget => {{
                            widgets[widget.id] = widget;
                        }});
                        
                        // Render the entire UI
                        const rootWidget = Object.values(widgets).find(w => w.type === 'RootContainer');
                        console.log('Root widget:', rootWidget);
                        if (rootWidget) {{
                            const rootElement = renderWidget(rootWidget.id);
                            console.log('Root element rendered:', rootElement);
                            document.getElementById('app').appendChild(rootElement);
                        }} else {{
                            console.error('Root widget not found!');
                        }}
                    }} else {{
                        console.error('No widgets in initial state!');
                    }}
                }}
                
                function handleUpdates(updates) {{
                    updates.forEach(update => {{
                        if (update.action === 'update') {{
                            if (!widgets[update.id]) {{
                                widgets[update.id] = {{
                                    id: update.id,
                                    properties: {{}}
                                }};
                            }}
                            widgets[update.id].properties[update.property] = update.value;
                            updateWidget(update.id, update.property);
                        }} else if (update.action === 'remove') {{
                            const element = document.getElementById(update.id);
                            if (element) {{
                                element.remove();
                            }}
                            delete widgets[update.id];
                        }}
                    }});
                }}
                
                function renderWidget(id) {{
                    console.log('Rendering widget with ID:', id);
                    const widget = widgets[id];
                    if (!widget) {{
                        console.error('Widget not found:', id);
                        return null;
                    }}
                    
                    const oldElement = document.getElementById(id);
                    console.log('Widget type:', widget.type, 'properties:', widget.properties);
                    
                    let element;
                    switch(widget.type) {{
                        case 'RootContainer':
                        case 'Container':
                            element = document.createElement('div');
                            element.className = 'pywt-container';
                            if (widget.type === 'RootContainer') {{
                                element.style.border = '1px solid #ccc';
                                element.style.padding = '10px';
                                element.style.borderRadius = '4px';
                            }}
                            
                            // Use the children array directly from the widget state
                            const childrenIds = widget.children || [];
                            console.log('Container ' + id + ' has ' + childrenIds.length + ' children:', childrenIds);
                                
                            // Render children
                            childrenIds.forEach(childId => {{
                                if (widgets[childId]) {{  // Make sure the child exists
                                    const childElement = renderWidget(childId);
                                    if (childElement) {{
                                        console.log('Appending child ' + childId + ' to parent ' + id);
                                        element.appendChild(childElement);
                                    }}
                                }} else {{
                                    console.error('Child widget not found:', childId);
                                }}
                            }});
                            break;
                            
                        case 'Button':
                            element = document.createElement('button');
                            element.className = 'pywt-button';
                            element.textContent = widget.properties.text || 'Button';
                            element.onclick = () => {{
                                sendEvent(id, 'click', {{}});
                            }};
                            break;
                            
                        case 'TextBox':
                            element = document.createElement('input');
                            element.className = 'pywt-textbox';
                            element.type = 'text';
                            element.value = widget.properties.value || '';
                            element.placeholder = widget.properties.placeholder || '';
                            element.oninput = (e) => {{
                                sendEvent(id, 'change', {{ value: e.target.value }});
                            }};
                            break;
                            
                        case 'Label':
                            element = document.createElement('div');
                            element.className = 'pywt-label';
                            element.textContent = widget.properties.text || '';
                            console.log('Label ' + id + ' text:', widget.properties.text);
                            break;
                            
                        default:
                            console.error('Unknown widget type: ' + widget.type);
                            return null;
                    }}
                    
                    element.id = id;
                    
                    if (oldElement && oldElement.parentElement) {{
                        oldElement.parentElement.replaceChild(element, oldElement);
                    }}
                    
                    return element;
                }}
                
                function updateWidget(id, property) {{
                    const widget = widgets[id];
                    const element = document.getElementById(id);
                    
                    if (!element || !widget) return;
                    
                    switch(widget.type) {{
                        case 'Label':
                            if (property === 'text') {{
                                element.textContent = widget.properties.text || '';
                            }}
                            break;
                            
                        case 'Button':
                            if (property === 'text') {{
                                element.textContent = widget.properties.text || 'Button';
                            }}
                            break;
                            
                        case 'TextBox':
                            if (property === 'value') {{
                                element.value = widget.properties.value || '';
                            }} else if (property === 'placeholder') {{
                                element.placeholder = widget.properties.placeholder || '';
                            }}
                            break;
                    }}
                }}
                
                function sendEvent(id, eventType, data) {{
                    if (ws && ws.readyState === WebSocket.OPEN) {{
                        console.log('Sending ' + eventType + ' event for widget ' + id, data);
                        const payload = JSON.stringify({{
                            event: {{
                                id: id,
                                type: eventType,
                                data: data
                            }}
                        }});
                        console.log('WebSocket sending:', payload);
                        ws.send(payload);
                    }} else {{
                        console.error('WebSocket not connected, cannot send event');
                        if (ws) {{
                            console.error('WebSocket state:', ws.readyState);
                        }}
                    }}
                }}
                
                window.onload = () => {{
                    console.log('Window loaded, connecting WebSocket');
                    connectWebSocket();
                    // Create app container if it doesn't exist
                    if (!document.getElementById('app')) {{
                        console.log('Creating app container');
                        document.body.appendChild(document.createElement('div')).id = 'app';
                    }}
                }};
            </script>
        </head>
        <body>
            <div id="app"></div>
        </body>
        </html>
        """
