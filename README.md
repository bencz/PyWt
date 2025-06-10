# PyWt: Python Web Toolkit

PyWt is a Python implementation inspired by [Wt (Web Toolkit) C++](https://www.webtoolkit.eu/wt), a mature and robust web development framework. PyWt is designed to bring the philosophy and programming paradigm of Wt to the Python ecosystem, allowing Python developers to build web applications using a widget-based approach similar to desktop GUI development, abstracting away the complexities of HTML, CSS, and JavaScript.

## Key Features

- **Widget-based Architecture**: Build web UIs with reusable Python widgets
- **Pure Python Development**: Create web applications entirely in Python
- **Async/Await Support**: 100% async/await-based implementation
- **WebSocket Communication**: Real-time communication between frontend and backend
- **Automatic State Synchronization**: Keeps frontend and backend state synchronized
- **Multi-Page Navigation**: Built-in page navigation system
- **Inspired by Wt C++**: Designed to follow the same paradigms and architecture of the original C++ framework

## Installation

```bash
pip install -r requirements.txt
```

## Minimal Example

```python
import asyncio
import sys
import os

# Add the parent directory to the path to import pywt ( running inside example folder )
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pywt.application import Application
from pywt.server import WServer
from pywt.navigation import Page
from pywt.widgets import Label, Button, TextBox, Container


class HomePage(Page):
    """Home page of the application"""
    def __init__(self, path="home", title="PyWt - Home"):
        super().__init__(path=path, title=title)
        self.set_property("visible", True)
        
        # Create a main container for the UI
        container = Container()
        self.add(container)
        
        # Add a title
        title = Label("PyWt Demo")
        title.set_property("style", "font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        container.add(title)
        
        # Add a text input field
        self.name_input = TextBox(placeholder="Your name")
        self.name_input.on_change.connect(self.on_name_changed)
        container.add(self.name_input)
        
        # Add a greeting label
        self.greeting = Label("")
        container.add(self.greeting)
        
        # Add a button that updates the greeting
        self.update_button = Button("Say Hello")
        self.update_button.on_click.connect(self.on_button_clicked)
        container.add(self.update_button)

    async def on_name_changed(self, event):
        """Handle the name input change event"""
        if self.name_input.text():
            self.greeting.set_text(f"Hello, {self.name_input.text()}!")
        else:
            self.greeting.set_text("")
            
    async def on_button_clicked(self, event):
        """Handle the button click event"""
        name = self.name_input.text()
        if name:
            self.greeting.set_text(f"Welcome to PyWt, {name}!")
        else:
            self.greeting.set_text("Please enter your name first.")


class MinimalApp(Application):
    """Minimal application with navigation"""
    def __init__(self):
        super().__init__()
        self.navigator.register_page("home", HomePage)
        self.navigator.set_default_page("home")


if __name__ == "__main__":
    server = WServer(MinimalApp, port=8080)
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("Server stopped by user")
```

## Architecture

PyWt follows an architecture similar to Wt C++, but adapted for Python's asynchronous programming paradigm:

- **Widget**: Base class for all UI components
- **Application**: Manages widgets and client connections
- **WServer**: HTTP/WebSocket server to serve the application
- **Signal/Event**: System for communication between widgets and event handlers

### Comparison with Wt C++

| Feature | PyWt | Wt C++ |
|-----------------|------|--------|
| Language | Python | C++ |
| Paradigm | Asynchronous (async/await) | Synchronous + threads |
| Communication | WebSockets | HTTP + WebSockets |
| Widgets | Simplified system | Complete system |
| Rendering | Client-side JavaScript | Hybrid Client/Server |

## Available Widgets

- **Container**: Basic container for grouping widgets
- **Label**: Text display
- **Button**: Clickable button
- **TextBox**: Text input field
- **RootContainer**: Special container used as UI root

## Documentation

For more examples and documentation, see the `examples` directory.

## Future Development

- More widget types
- Advanced CSS support
- Page routing
- Modal dialogs
- Frontend framework integration
