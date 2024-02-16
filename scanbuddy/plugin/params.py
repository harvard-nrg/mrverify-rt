import os
import re
import pydicom
import logging
import scanbuddy.scanner as scanner

logger = logging.getLogger('params')

class Plugin:
    def __init__(self, app, db, metadata, params):
        self.app = app
        self.critical = (False, None, False)
        self._db = db
        self._metadata = metadata
        self._params = params
        self._isregex = re.compile('regex\((.*)\)')

    def run(self):
        errors = list()
        Scanner = None
        files = os.listdir(self._db)
        num_files = len(files)
        for f in files:
            fullfile = os.path.join(self._db, f)
            ds = pydicom.dcmread(fullfile, stop_before_pixels=True)
            name = ds.PatientName
            series = ds.SeriesNumber
            description = ds.SeriesDescription
            ds.num_files = num_files
            if not Scanner:
                Scanner = scanner.get(ds)
            ds = Scanner(ds)
            for key,params in iter(self._params.items()):
                expecting = params['expecting']
                message = params.get('message', 'no message?')
                bsod = params.get('bsod', False)
                # check if expected value is a regex
                regex = self._isregex.match(str(expecting))
                if regex:
                    expecting = regex.group(1).strip()
                actual = getattr(ds, key)()
                try:
                    if regex:
                        assert re.match(expecting, actual) != None
                    else:
                        assert actual == expecting
                except AssertionError as e:
                    if (series, key) in errors:
                        continue
                    errors.append((series, key))
                    self.critical = (True, message, bsod)
                    details = f'{name}, scan {series}, {description} - {key} - expected "{expecting}" but found "{actual}"'
                    self.app.call_from_thread(
                        self.app.logger.error,
                        f'[bold red blink]{details}[/]'
                    )

