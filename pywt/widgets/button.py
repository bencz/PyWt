"""
Button widget for PyWt
"""
from typing import Optional, Dict, Any, Callable
from ..widget import Widget, Event


class Button(Widget):
    """A clickable button widget"""
    def __init__(self, text: str = "Button"):
        super().__init__()
        self.set_property("type", "Button")
        self.set_property("text", text)
        
    def render_html(self) -> str:
        """Render the button to HTML"""
        text = self.get_property("text", "Button")
        return f'<button id="{self.id}" class="pywt-button">{text}</button>'
        
    def set_text(self, text: str) -> 'Button':
        """Set the text of the button"""
        self.set_property("text", text)
        return self
        
    def text(self) -> str:
        """Get the text of the button"""
        return self.get_property("text", "Button")
