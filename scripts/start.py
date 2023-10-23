#!/usr/bin/env python3 -u

import scanbuddy
import multiprocessing
from textual.app import App
import scanbuddy.config as config
from scanbuddy.cstore import CStore
from argparse import ArgumentParser
from textual.widgets import Header, Footer
from scanbuddy.ui.widgets import Logger
from scanbuddy.ui.screens.bsod import BSOD
from scanbuddy.alerts import Audio

class ScanBuddy(App):
    BINDINGS = [
        ('q', 'quit', 'Quit')
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

    def compose(self):
        self.parse_args()
        self.logger = Logger(markup=True)
        self.logger.max_lines = self.args.scrollback
        yield Header()
        yield self.logger
        yield Footer()

    def on_ready(self) -> None:
        self.logger.info(f'Welcome to ScanBuddy {scanbuddy.version()}')
        CStore(self).run()

    def chime(self) -> None:
        Audio().chime()

    def bsod(self, message) -> None:
        screen = BSOD(message)
        self.push_screen(screen)
 
if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    app = ScanBuddy()
    app.run()
