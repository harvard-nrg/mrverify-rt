from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button

ERROR_ART = """
     ██╗    ██╗ █████╗ ██████╗ ███╗   ██╗██╗███╗   ██╗ ██████╗ 
     ██║    ██║██╔══██╗██╔══██╗████╗  ██║██║████╗  ██║██╔════╝ 
     ██║ █╗ ██║███████║██████╔╝██╔██╗ ██║██║██╔██╗ ██║██║  ███╗
     ██║███╗██║██╔══██║██╔══██╗██║╚██╗██║██║██║╚██╗██║██║   ██║
     ╚███╔███╔╝██║  ██║██║  ██║██║ ╚████║██║██║ ╚████║╚██████╔╝
      ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
"""

class BSOD(Screen):
    BINDINGS = [('escape', 'app.pop_screen', 'Pop screen')]
    CSS_PATH = 'bsod.tcss'

    def __init__(self, message, title=None, *args, **kwargs):
        self._message = message
        self._title = title or 'Scan Buddy'
        super(BSOD, self).__init__(*args, **kwargs)
        
    def compose(self) -> ComposeResult:
        yield Static(f' {self._title} ', id='title')
        yield Static(f'[blink]{ERROR_ART}[/]')
        yield Static(self._message)
        yield Button('Dismiss')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()
