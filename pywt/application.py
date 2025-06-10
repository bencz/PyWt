"""
Application class for PyWt framework
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Callable, Awaitable
from .widget import Widget
from .widgets.container import Container
from .navigation import Navigator, Page


class RootContainer(Container):
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
        
        # Initialize navigation
        self.navigator = Navigator(self)
        
        # Static files path
        self._static_path = Path(__file__).parent / "static"
        
    async def initialize(self) -> None:
        """Initialize the application"""
        # Initialize navigation if pages are registered
        if hasattr(self.navigator, 'default_page') and self.navigator.default_page:
            await self.navigator.initialize()
            
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
        # Sempre incluir o RootContainer
        widgets_state = [self.root.get_initial_state()]
        
        # Filtrar páginas visíveis
        visible_pages = []
        for child in self.root.children:
            # Se for uma página, verificar se está visível
            if isinstance(child, Page):
                is_visible = child.get_property("visible", False)
                if is_visible:
                    visible_pages.append(child)
                    # Coletar estado da página visível e seus filhos
                    widgets_state.extend(self._collect_widget_states_from(child))
            else:
                # Se não for uma página, incluir normalmente
                widgets_state.extend(self._collect_widget_states_from(child))
        
        print(f"Sending initial state with {len(widgets_state)} widgets, {len(visible_pages)} visible pages")
        
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
        
    def _collect_widget_states_from(self, widget: Widget) -> List[Dict[str, Any]]:
        """Collect the state of a widget and its children without including the widget itself"""
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
            
            # Handle navigation events
            if widget_id == "navigation" and event_type == "navigate":
                path = event_value.get("path", "")
                if path:
                    await self.navigator.navigate_to(path)
                return
                
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
        # Determine application title from current page or default
        title = "PyWt Application"
        if hasattr(self.navigator, 'current_page') and self.navigator.current_page:
            page_title = self.navigator.current_page.get_property("title")
            if page_title:
                title = page_title
                
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="stylesheet" href="/static/css/pywt.css">
            <script src="/static/js/pywt.js"></script>
        </head>
        <body>
            <div id="app"></div>
        </body>
        </html>
        """
        
    def get_static_file_content(self, path: str) -> tuple[Optional[str], Optional[str]]:
        """Get the content of a static file
        
        Returns:
            tuple: (content, content_type) or (None, None) if file not found
        """
        full_path = self._static_path / path.lstrip('/')
        
        # Security check to prevent directory traversal
        try:
            full_path = full_path.resolve()
            if not str(full_path).startswith(str(self._static_path)):
                return None, None
        except (ValueError, RuntimeError):
            return None, None
            
        if not full_path.exists() or not full_path.is_file():
            return None, None
            
        # Determine content type based on file extension
        content_type = "text/plain"
        if full_path.suffix == ".css":
            content_type = "text/css"
        elif full_path.suffix == ".js":
            content_type = "application/javascript"
        elif full_path.suffix in (".jpg", ".jpeg"):
            content_type = "image/jpeg"
        elif full_path.suffix == ".png":
            content_type = "image/png"
        elif full_path.suffix == ".svg":
            content_type = "image/svg+xml"
            
        try:
            with open(full_path, "r") as f:
                content = f.read()
            return content, content_type
        except Exception as e:
            print(f"Error reading static file {full_path}: {e}")
            return None, None
            
    async def initialize(self) -> None:
        """Initialize the application"""
        # Initialize navigation if pages are registered
        if hasattr(self.navigator, 'default_page'):
            await self.navigator.initialize()
