"""
Label widget for PyWt
"""
from typing import Optional, Dict, Any
from ..widget import Widget


class Label(Widget):
    """A simple text label widget"""
    def __init__(self, text: str = ""):
        super().__init__()
        self.set_property("type", "Label")
        self.set_property("text", text)
        
    def render_html(self) -> str:
        """Render the label to HTML"""
        text = self.get_property("text", "")
        return f'<div id="{self.id}" class="pywt-label">{text}</div>'
        
    def set_text(self, text: str) -> None:
        """Set the text of the label"""
        self.set_property("text", text)
        
    def text(self) -> str:
        """Get the text of the label"""
        return self.get_property("text", "")
