"""
Hello World example for PyWt

This example demonstrates the basic features of PyWt including state synchronization
between frontend and backend using WebSockets.
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import pywt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pywt.application import Application
from pywt.server import WServer
from pywt.navigation import Page
from pywt.widgets import Label, Button, TextBox, Container


class HomePage(Page):
    """Home page for the Hello World application"""
    def __init__(self, path="home", title="PyWt - Hello World"):
        super().__init__(path=path, title=title)

    def __postinit__(self):
        # Create a main container for our UI
        container = Container()
        self.add(container)
        
        # Add a title
        title = Label("PyWt Demo Application")
        title.set_property("style", "font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        container.add(title)
        
        # Add a text input with label
        input_label = Label("Enter your name:")
        container.add(input_label)
        
        self.name_input = TextBox(placeholder="Your name")
        self.name_input.on_change.connect(self.on_name_changed)
        container.add(self.name_input)
        
        # Add a greeting label that will be updated
        self.greeting = Label("")
        container.add(self.greeting)
        
        # Add a button that will update the greeting
        self.update_button = Button("Say Hello")
        self.update_button.on_click.connect(self.on_button_clicked)
        container.add(self.update_button)
        
        # Add another button to clear the input
        clear_button = Button("Clear")
        clear_button.on_click.connect(self.on_clear_clicked)
        container.add(clear_button)
        
        # Counter example to show real-time updates
        counter_container = Container()
        container.add(counter_container)
        
        counter_title = Label("Automatic Counter:")
        counter_container.add(counter_title)
        
        self.counter_label = Label("0")
        counter_container.add(self.counter_label)
        
        # Start the counter
        self.count = 0
        self._counter_task = asyncio.create_task(self._run_counter())
        

    async def on_name_changed(self, event):
        """Handle the name input change event"""
        # This will be called whenever the user types in the text box
        print(f"Name changed to: {self.name_input.text()}")
        
        # We could update the greeting in real-time here if we wanted to
        if self.name_input.text():
            self.greeting.set_text(f"Hello, {self.name_input.text()}! (Press the button to confirm)")
        else:
            self.greeting.set_text("")
            
    async def on_button_clicked(self, event):
        """Handle the button click event"""
        name = self.name_input.text()
        if name:
            self.greeting.set_text(f"Hello, {name}! Welcome to PyWt!")
        else:
            self.greeting.set_text("Please enter your name first.")
            
    async def on_clear_clicked(self, event):
        """Handle the clear button click event"""
        print("Clearing input and greeting")
        self.name_input.set_text("")
        self.greeting.set_text("")
        self.counter_label.set_text("0")
        self.count = 0
        
    async def _run_counter(self):
        """Run a counter to demonstrate automatic updates"""
        while True:
            await asyncio.sleep(1)
            self.count += 1
            self.counter_label.set_text(str(self.count))


class HelloApp(Application):
    """Main application class that sets up the navigation"""
    def __init__(self):
        super().__init__()
        # Registrar a página inicial
        self.navigator.register_page("home", HomePage)
        # Definir a página inicial como padrão
        self.navigator.set_default_page("home")


if __name__ == "__main__":
    server = WServer(HelloApp, port=8080)
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("Server stopped by user")
