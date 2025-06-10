"""
Navigation link widget for PyWt framework
"""
from typing import Optional
from ..widget import Widget


class NavLink(Widget):
    """Navigation link widget for PyWt applications"""
    def __init__(self, text: str = "", path: str = ""):
        super().__init__()
        self.set_property("type", "NavLink")
        self.set_property("text", text)
        self.set_property("path", path)
        
    def set_text(self, text: str) -> 'NavLink':
        """Set the text of the navigation link"""
        self.set_property("text", text)
        return self
        
    def set_path(self, path: str) -> 'NavLink':
        """Set the path to navigate to when clicked"""
        self.set_property("path", path)
        return self
        
    def render_html(self) -> str:
        """Render the navigation link to HTML"""
        text = self.get_property("text", "Link")
        path = self.get_property("path", "")
        return f'<a href="#{path}" class="pywt-nav-link" id="{self.id}">{text}</a>'
