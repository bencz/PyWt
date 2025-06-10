"""
Container widget for PyWt
"""
from typing import Optional, Dict, Any
from ..widget import Widget


class Container(Widget):
    """A container widget that can hold other widgets"""
    def __init__(self, id: Optional[str] = None):
        super().__init__()
        if id:
            self.id = id
        self.set_property("type", "Container")
        
    def render_html(self) -> str:
        """Render the container to HTML"""
        html = f'<div id="{self.id}" class="pywt-container">'
        for child in self.children:
            html += child.render_html()
        html += '</div>'
        return html
        
    def get_initial_state(self) -> Dict[str, Any]:
        """Get the initial state of the container"""
        state = super().get_initial_state()
        state["children"] = [child.id for child in self.children]
        return state
