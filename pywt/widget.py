"""
Base widget class for PyWt framework
"""
import uuid
from typing import Dict, List, Optional, Any, Set, Callable


class Event:
    """Base event class for widget events"""
    def __init__(self, sender, event_type: str, data: Optional[Dict[str, Any]] = None):
        self.sender = sender
        self.event_type = event_type
        self.data = data or {}


class Signal:
    """Signal class for handling widget events"""
    def __init__(self, name: str):
        self.name = name
        self.handlers: List[Callable] = []
        
    def connect(self, handler: Callable) -> None:
        """Connect a handler function to the signal"""
        self.handlers.append(handler)
        
    def disconnect(self, handler: Callable) -> None:
        """Disconnect a handler function from the signal"""
        if handler in self.handlers:
            self.handlers.remove(handler)
            
    async def emit(self, event: Event) -> None:
        """Emit the signal with an event"""
        for handler in self.handlers:
            await handler(event)


class Widget:
    """Base widget class for all PyWt components"""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.parent = None
        self.children: List['Widget'] = []
        self.app = None
        self._rendered = False
        self._properties: Dict[str, Any] = {}
        self._dirty_properties: Set[str] = set()
        
        # Create signals for common events
        self.on_click = Signal("click")
        self.on_change = Signal("change")
        
    def add(self, child: 'Widget') -> 'Widget':
        """Add a child widget to this widget"""
        if child.parent:
            child.parent.remove(child)
        child.parent = self
        child.set_property("parent", self.id)  # Store parent ID in properties for client
        self.children.append(child)
        if self.app:
            child._set_application(self.app)
        return child
        
    def remove(self, child: 'Widget') -> None:
        """Remove a child widget from this widget"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            if self.app:
                self.app._schedule_update({
                    "action": "remove",
                    "id": child.id
                })
                
    def _set_application(self, app) -> None:
        """Set the application instance for this widget and its children"""
        self.app = app
        app.register_widget(self)  # Registrar este widget na aplicação
        for child in self.children:
            child._set_application(app)
            
    def set_property(self, name: str, value: Any) -> None:
        """Set a property value and mark it as dirty"""
        self._properties[name] = value
        self._dirty_properties.add(name)
        if self.app:
            self.app._schedule_update({
                "action": "update",
                "id": self.id,
                "property": name,
                "value": value
            })
            
    def get_property(self, name: str, default: Any = None) -> Any:
        """Get a property value"""
        return self._properties.get(name, default)
        
    def render_html(self) -> str:
        """Render the widget to HTML (must be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement render_html")
        
    def render_js(self) -> str:
        """Render widget-specific JavaScript (can be implemented by subclasses)"""
        return ""
        
    def get_initial_state(self) -> Dict[str, Any]:
        """Get the initial state of the widget for the client"""
        state = {
            "id": self.id,
            "type": self.__class__.__name__,
            "properties": dict(self._properties),  # Create a copy to avoid reference issues
            "children": [child.id for child in self.children]  # Include children IDs
        }
        
        # Ensure parent ID is set in properties
        if self.parent and "parent" not in state["properties"]:
            state["properties"]["parent"] = self.parent.id
            
        return state
        
    async def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Handle an event from the client"""
        print(f"Widget {self.id} ({self.__class__.__name__}) handling event: {event_type}")
        event = Event(self, event_type, data)
        
        if event_type == "click":
            print(f"Processing click event, has on_click: {hasattr(self, 'on_click')}")
            if hasattr(self, "on_click"):
                print(f"Click event has {len(self.on_click.handlers)} handlers")
                await self.on_click.emit(event)
            else:
                print(f"Widget does not have on_click signal")
                
        elif event_type == "change":
            print(f"Processing change event, has on_change: {hasattr(self, 'on_change')}")
            # Update the property from client data
            if "value" in data:
                old_value = self.get_property("value", "")
                self.set_property("value", data["value"])
                print(f"Updated value from '{old_value}' to '{data['value']}'")
                
            if hasattr(self, "on_change"):
                print(f"Change event has {len(self.on_change.handlers)} handlers")
                await self.on_change.emit(event)
            else:
                print(f"Widget does not have on_change signal")
