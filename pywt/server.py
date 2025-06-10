"""
Server implementation for PyWt applications
"""
import asyncio
import json
import logging
import pathlib
from typing import Type, Dict, Any, Optional, Callable
from aiohttp import web
from aiohttp.web import WebSocketResponse

from .application import Application

logger = logging.getLogger(__name__)


class WServer:
    """Web server for PyWt applications"""
    def __init__(self, app_class: Type[Application], host: str = "localhost", port: int = 8080):
        self.app_class = app_class
        self.host = host
        self.port = port
        self.web_app = web.Application()
        self.web_app.add_routes([
            web.get('/', self.handle_index),
            web.get('/ws', self.handle_websocket),
            web.get('/static/{path:.*}', self.handle_static),
            web.get('/{path:.*}', self.handle_page),
        ])
        self.clients: Dict[WebSocketResponse, Application] = {}
        
    async def handle_index(self, request: web.Request) -> web.Response:
        """Handle the index page request"""
        app_instance = self.app_class()
        # Initialize the application
        if hasattr(app_instance, 'initialize'):
            await app_instance.initialize()
        html = app_instance.get_html()
        return web.Response(text=html, content_type='text/html')
        
    async def handle_websocket(self, request: web.Request) -> WebSocketResponse:
        """Handle WebSocket connections"""
        print("WebSocket connection requested")
        ws = WebSocketResponse()
        await ws.prepare(request)
        
        print("WebSocket prepared, creating application instance")
        # Create a new application instance for this client
        app_instance = self.app_class()
        # Initialize the application
        if hasattr(app_instance, 'initialize'):
            await app_instance.initialize()
        self.clients[ws] = app_instance
        
        # Register the websocket with the application
        print("Registering websocket with application")
        await app_instance.connect_client(ws)
        print("Client connected and initial state sent")
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await app_instance.handle_client_message(data)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON received: {msg.data}")
                    except Exception as e:
                        logger.error(f"Error handling message: {e}")
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
        finally:
            # Clean up when the connection is closed
            app_instance.disconnect_client(ws)
            if ws in self.clients:
                del self.clients[ws]
                
        return ws
        
    async def handle_static(self, request: web.Request) -> web.Response:
        """Handle static file requests"""
        path = request.match_info['path']
        app_instance = self.app_class()
        content, content_type = app_instance.get_static_file_content(path)
        
        if content is None:
            return web.Response(text="File not found", status=404)
        
        return web.Response(text=content, content_type=content_type)
        
    async def handle_page(self, request: web.Request) -> web.Response:
        """Handle page requests"""
        path = request.match_info['path']
        app_instance = self.app_class()
        
        # Initialize the application
        if hasattr(app_instance, 'initialize'):
            await app_instance.initialize()
        
        # If the path is for a registered page, navigate to it
        if hasattr(app_instance.navigator, 'pages') and path in app_instance.navigator.pages:
            await app_instance.navigator.navigate_to(path)
        
        html = app_instance.get_html()
        return web.Response(text=html, content_type='text/html')
        
    async def run(self) -> None:
        """Run the server"""
        runner = web.AppRunner(self.web_app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        print(f"Starting server at http://{self.host}:{self.port}")
        await site.start()
        
        # Keep the server running
        while True:
            await asyncio.sleep(3600)  # Sleep for a long time
