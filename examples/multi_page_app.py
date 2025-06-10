"""
Example of a multi-page application using PyWt
"""
import asyncio
import sys
import os

# Add the parent directory to the path so we can import pywt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pywt.application import Application
from pywt.server import WServer
from pywt.navigation import Page
from pywt.widgets.button import Button
from pywt.widgets.textbox import TextBox
from pywt.widgets.label import Label
from pywt.widgets.navlink import NavLink


class HomePage(Page):
    """Home page of the application"""
    def __init__(self, path: str = "", title: str = ""):
        super().__init__(path=path, title=title)
        self.set_property("type", "HomePage")
        
        # Create a welcome message
        self.add(Label("Bem-vindo ao PyWt Multi-Page App!").set_property("text_size", "large"))
        self.add(Label("Este é um exemplo de aplicação com múltiplas páginas."))
        
        # Create navigation links
        self.add(Label("Navegue para:"))
        self.add(NavLink("Página Sobre", "about"))
        self.add(NavLink("Página de Contato", "contact"))
        
        # Create a counter button
        self.counter = 0
        self.counter_label = Label(f"Contador: {self.counter}")
        self.add(self.counter_label)
        
        self.counter_button = Button("Incrementar Contador")
        self.counter_button.on_click.connect(self.increment_counter)
        self.add(self.counter_button)
        
    async def increment_counter(self, event):
        """Increment the counter when the button is clicked"""
        self.counter += 1
        self.counter_label.set_property("text", f"Contador: {self.counter}")


class AboutPage(Page):
    """About page of the application"""
    def __init__(self, path: str = "", title: str = ""):
        super().__init__(path=path, title=title)
        self.set_property("type", "AboutPage")
        
        # Create content
        self.add(Label("Sobre o PyWt").set_property("text_size", "large"))
        self.add(Label("PyWt é um framework web Python inspirado no Wt C++."))
        self.add(Label("Principais características:"))
        self.add(Label("- Programação orientada a eventos"))
        self.add(Label("- Widgets reutilizáveis"))
        self.add(Label("- Suporte a múltiplas páginas"))
        self.add(Label("- CSS e JS em arquivos estáticos"))
        
        # Navigation
        self.add(Label(""))  # Spacer
        self.add(NavLink("Voltar para Home", "home"))
        self.add(NavLink("Ir para Contato", "contact"))


class ContactPage(Page):
    """Contact page of the application"""
    def __init__(self, path: str = "", title: str = ""):
        super().__init__(path=path, title=title)
        self.set_property("type", "ContactPage")
        
        # Create content
        self.add(Label("Entre em Contato").set_property("text_size", "large"))
        self.add(Label("Preencha o formulário abaixo para entrar em contato:"))
        
        self.add(Label("Nome:"))
        self.name_input = TextBox()
        self.name_input.set_placeholder("Seu nome")
        self.add(self.name_input)
        
        self.add(Label("Email:"))
        self.email_input = TextBox()
        self.email_input.set_placeholder("seu.email@exemplo.com")
        self.add(self.email_input)
        
        self.add(Label("Mensagem:"))
        self.message_input = TextBox()
        self.message_input.set_placeholder("Sua mensagem")
        self.add(self.message_input)
        
        self.submit_button = Button("Enviar")
        self.submit_button.on_click.connect(self.submit_form)
        self.add(self.submit_button)
        
        self.result_label = Label("")
        self.add(self.result_label)
        
        # Navigation
        self.add(Label(""))  # Spacer
        self.add(NavLink("Voltar para Home", "home"))
        self.add(NavLink("Ir para Sobre", "about"))
        
    async def submit_form(self, event):
        """Handle form submission"""
        name = self.name_input.get_property("value", "")
        email = self.email_input.get_property("value", "")
        message = self.message_input.get_property("value", "")
        
        if not name or not email or not message:
            self.result_label.set_property("text", "Por favor, preencha todos os campos!")
            return
            
        # In a real app, you would send this data to a server
        self.result_label.set_property("text", f"Obrigado, {name}! Sua mensagem foi enviada e iremos encaminhar o e-mail com a resposta para {email}.")
        
        # Clear the form
        self.name_input.set_property("value", "")
        self.email_input.set_property("value", "")
        self.message_input.set_property("value", "")


class MultiPageApp(Application):
    """Multi-page application example"""
    def __init__(self):
        super().__init__()
        
        # Register pages with the navigator
        self.navigator.register_page("home", HomePage, "PyWt - Home")
        self.navigator.register_page("about", AboutPage, "PyWt - Sobre")
        self.navigator.register_page("contact", ContactPage, "PyWt - Contato")
        
        # Set the default page
        self.navigator.set_default_page("home")


async def main():
    """Run the application"""
    server = WServer(MultiPageApp, host="localhost", port=8080)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
