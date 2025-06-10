"""
Navigation system for PyWt framework
"""
import asyncio
from typing import Dict, Any, Callable, Optional, List, Type
from .widget import Widget
from .widgets.container import Container


class Page(Container):
    """Base class for pages in a multi-page application"""
    def __init__(self, path: str = "", title: str = ""):
        super().__init__()
        self.path = path
        self.set_property("type", "Page")
        self.set_property("title", title)
        self.set_property("path", path)
        
    def on_navigation_to(self) -> None:
        """Called when navigation to this page occurs"""
        pass
        
    def on_navigation_from(self) -> None:
        """Called when navigation away from this page occurs"""
        pass


class Navigator:
    """Navigation manager for PyWt applications"""
    def __init__(self, app):
        self.app = app
        self.pages: Dict[str, Page] = {}
        self.current_page: Optional[Page] = None
        self.default_page: Optional[str] = None
        self.history: List[str] = []
        
    def register_page(self, path: str, page_class: Type[Page], title: str = "") -> None:
        """Register a page with the navigator"""
        # Create page instance
        page = page_class(path=path, title=title)
        
        # Add page to the application's root container
        self.app.root.add(page)
        
        # Set page as invisible initially
        page.set_property("visible", False)
        
        # Register page in the navigator
        self.pages[path] = page
        
        # Set as default page if it's the first one registered
        if not self.default_page:
            self.default_page = path
            
        print(f"Registered page '{path}' with title '{title}', visible: {page.get_property('visible', False)}")
            
    def set_default_page(self, path: str) -> None:
        """Set the default page to navigate to when no path is specified"""
        if path in self.pages:
            self.default_page = path
        else:
            raise ValueError(f"Page with path '{path}' not registered")
            
    async def navigate_to(self, path: str) -> None:
        """Navigate to a specific page"""
        if path not in self.pages:
            print(f"Page {path} not found")
            return
            
        print(f"Processing navigation to path: {path}")
        
        # Chamar o método on_navigation_from da página atual, se existir
        if self.current_page and hasattr(self.current_page, "on_navigation_from"):
            method = self.current_page.on_navigation_from
            if asyncio.iscoroutinefunction(method):
                await method()
            else:
                method()
        
        # Ocultar todas as páginas
        for page in self.pages.values():
            page.set_property("visible", False)
        
        # Atualizar a página atual e torná-la visível
        old_page = self.current_page
        self.current_page = self.pages[path]
        self.current_page.set_property("visible", True)
        
        # Atualizar o histórico
        if old_page:
            self.history.append(old_page.path)
        
        # Chamar o método on_navigation_to da nova página, se existir
        if hasattr(self.current_page, "on_navigation_to"):
            method = self.current_page.on_navigation_to
            if asyncio.iscoroutinefunction(method):
                await method()
            else:
                method()
        
        # Enviar uma atualização para o cliente
        self.app._schedule_update({
            "action": "navigation",
            "path": path,
            "title": self.current_page.get_property("title", "")
        })
        self._send_page_widgets()
        
    async def initialize(self) -> None:
        """Initialize the navigator with the default page"""
        if self.default_page:
            await self.navigate_to(self.default_page)
    
    def _send_page_widgets(self) -> None:
        """Envia os widgets da página atual para o cliente"""
        if not self.current_page:
            return
            
        # Coletar os widgets da página atual
        page_widgets = self.app._collect_widget_states(self.current_page)
        
        # Enviar todos os widgets em uma única atualização
        self.app._schedule_update({
            "action": "page_widgets",
            "page_path": self.current_page.path,
            "widgets": page_widgets
        })
        
        print(f"Enviando {len(page_widgets)} widgets da página {self.current_page.path}")
        # Registrar os IDs dos widgets para debug
        for widget in page_widgets:
            print(f"  - Widget: {widget['id']}, tipo: {widget.get('type', '?')}")

    
    async def navigate_back(self) -> None:
        """Navigate to the previous page in history"""
        if len(self.history) > 1:
            # Remove current page from history
            self.history.pop()
            # Get previous page
            previous_path = self.history[-1]
            # Remove it from history as navigate_to will add it again
            self.history.pop()
            # Navigate to previous page
            await self.navigate_to(previous_path)
        
    async def initialize(self) -> None:
        """Initialize navigation with default page"""
        if self.default_page:
            await self.navigate_to(self.default_page)
        else:
            raise ValueError("No default page set for navigation")
