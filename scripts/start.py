#!/usr/bin/env python3 -u

from argparse import ArgumentParser
from textual.app import App
from textual.widgets import Header, Footer
import scanbuddy
import scanbuddy.config as config
from scanbuddy.cstore import CStore
from scanbuddy.ui.widgets import Logger
from scanbuddy.ui.screens.bsod import BSOD
from scanbuddy.alerts import Audio

class ScanBuddy(App):
    BINDINGS = [
        ('q', 'quit', 'Quit'),
        ('c', 'clear', 'Clear')
    ]

    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument('-c', '--config', default='config.yaml')#required=True)
        parser.add_argument('--address', default='0.0.0.0')
        parser.add_argument('--port', default=11112, type=int)
        parser.add_argument('--ae-title', default='SCANBUDDY')
        parser.add_argument('--cache', default='~/.cache')
        parser.add_argument('--no-sound', action='store_true')
        parser.add_argument('--scrollback', type=int, default=5000)
        parser.add_argument('-v', '--verbose', action='store_true')
        self.args = parser.parse_args()
        config.no_sound = self.args.no_sound

    def action_clear(self) -> None:
        self.logger.clear()
        self.logger.info(self.welcome)

    def compose(self) -> None:
        self.welcome = f'Welcome to ScanBuddy {scanbuddy.version()}'
        self.parse_args()
        self.logger = Logger(markup=True, highlight=True, wrap=True)
        self.logger.max_lines = self.args.scrollback
        yield Header()
        yield self.logger
        yield Footer()

    def on_ready(self) -> None:
        self.logger.info(self.welcome)
        CStore(self).run()

    def chime(self) -> None:
        Audio().chime()

    def bsod(self, message, title=None) -> None:
        screen = BSOD(message, title)
        self.push_screen(screen)
 
if __name__ == '__main__':
    app = ScanBuddy()
    app.run()
