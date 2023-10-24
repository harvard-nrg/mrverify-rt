import os
import shutil
import logging
from threading import Timer

import scanbuddy.plugin
import scanbuddy.scanner
from scanbuddy.config import Config
from rich.panel import Panel

logger = logging.getLogger(__name__)

class SeriesIngress:
    def __init__(self, app, conf, cache='~/.cache/scanbuddy', wait=5):
        self.app = app
        self._conf = Config(conf)
        self._cache = os.path.expanduser(cache)
        self._wait = wait
        self._db = None
        self._example = None
        self._cleanup_callbacks = list()
        self._start_timer()
        self._errors = None

    def _start_timer(self):
        self._timer = Timer(self._wait, self._process)
        self._timer.start()

    def _reset_timer(self):
        self._timer.cancel()
        self._start_timer()

    def _create_db(self, ds):
        basename = f'{ds.StudyInstanceUID}-{ds.SeriesNumber}'
        self._db = os.path.join(self._cache, basename)
        os.makedirs(self._db, exist_ok=True)

    def save(self, ds):
        if not self._example:
            self._example = ds.copy()
        if not self._db:
            self._create_db(ds)
        basename = f'{ds.SOPInstanceUID}.dcm'
        saveas = os.path.join(self._db, basename)
        ds.save_as(saveas, write_like_original=False)
        self._reset_timer()

    def cleanup(self):
        if os.path.exists(self._db):
            shutil.rmtree(self._db)
            self._db = None
        for f in self._cleanup_callbacks:
            f()
 
    def _process(self):
        series = self._example.SeriesNumber
        Scanner = scanbuddy.scanner.get(self._example)
        plugins = self._conf.select(Scanner(self._example))
        try:
            for name,params in iter(plugins.items()):
                plugin = scanbuddy.plugin.load(name)(self.app, self._db, self._example, params)
                self.app.call_from_thread(
                    self.app.logger.info,
                    f'running plugin {name} on scan {series}'
                )
                plugin.run()
                err, message, bsod = plugin.critical
                if err:
                    self.app.call_from_thread(self.app.chime)
                    self.app.call_from_thread(
                        self.app.logger.write,
                        Panel(f'[bold red]{message.strip()}[/]')
                    )
                    if bsod:
                        self.app.call_from_thread(
                            self.app.bsod,
                            message,
                            title=self._example.PatientName
                        )
        finally:
            self.cleanup()

    def register_cleanup_callback(self, f):
        self._cleanup_callbacks.append(f)

