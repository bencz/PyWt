# PyWt: Python Web Toolkit

PyWt is a Python implementation inspired by [Wt (Web Toolkit) C++](https://www.webtoolkit.eu/wt), a mature and robust web development framework. PyWt is designed to bring the philosophy and programming paradigm of Wt to the Python ecosystem, allowing Python developers to build web applications using a widget-based approach similar to desktop GUI development, abstracting away the complexities of HTML, CSS, and JavaScript.

## Key Features

- **Widget-based Architecture**: Build web UIs with reusable Python widgets
- **Pure Python Development**: Create web applications entirely in Python
- **Async/Await Support**: 100% async/await-based implementation
- **WebSocket Communication**: Real-time communication between frontend and backend
- **Automatic State Synchronization**: Keeps frontend and backend state synchronized
- **Inspired by Wt C++**: Designed to follow the same paradigms and architecture of the original C++ framework

## Installation

```bash
pip install -r requirements.txt
```

## Simple Example

```python
import asyncio
from pywt import Application, WServer
from pywt.widgets import Label, Button, TextBox, Container

class HelloApp(Application):
    def __init__(self):
        super().__init__()
        
        container = Container()
        self.root.add(container)
        
        self.label = Label("Hello, PyWt!")
        container.add(self.label)
        
        self.textbox = TextBox()
        self.textbox.on_change.connect(self.on_text_changed)
        container.add(self.textbox)
        
        button = Button("Click me!")
        button.on_click.connect(self.on_button_clicked)
        container.add(button)
        
    async def on_button_clicked(self, event):
        self.label.set_text(f"Button clicked! Text is: {self.textbox.text()}")
        
    async def on_text_changed(self, event):
        print(f"Text changed to: {self.textbox.text()}")

if __name__ == "__main__":
    server = WServer(HelloApp, port=8080)
    asyncio.run(server.run())
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
