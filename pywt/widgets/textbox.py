"""
TextBox widget for PyWt
"""
from typing import Optional, Dict, Any, Callable
from ..widget import Widget, Event


class TextBox(Widget):
    """A text input widget with automatic state synchronization"""
    def __init__(self, initial_value: str = "", placeholder: str = ""):
        super().__init__()
        self.set_property("type", "TextBox")
        self.set_property("value", initial_value)
        self.set_property("placeholder", placeholder)
        
    def render_html(self) -> str:
        """Render the textbox to HTML"""
        value = self.get_property("value", "")
        placeholder = self.get_property("placeholder", "")
        placeholder_attr = f' placeholder="{placeholder}"' if placeholder else ''
        return f'<input id="{self.id}" class="pywt-textbox" type="text" value="{value}"{placeholder_attr}/>'
        
    def set_value(self, value: str) -> None:
        """Set the value of the textbox"""
        self.set_property("value", value)
        
    def value(self) -> str:
        """Get the current value of the textbox"""
        return self.get_property("value", "")
        
    def text(self) -> str:
        """Alias for value() to maintain API compatibility with other widgets"""
        return self.value()
        
    def set_text(self, text: str) -> None:
        """Alias for set_value() to maintain API compatibility with other widgets"""
        self.set_value(text)
        
    def set_placeholder(self, placeholder: str) -> None:
        """Set the placeholder text"""
        self.set_property("placeholder", placeholder)
        
    def placeholder(self) -> str:
        """Get the placeholder text"""
        return self.get_property("placeholder", "")
        
    async def handle_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Handle an event from the client"""
        if event_type == "change" and "value" in data:
            self.set_property("value", data["value"])
            event = Event(self, event_type, data)
            await self.on_change.emit(event)
