import os
import re
import pydicom
import logging
from termcolor import colored

from scanbuddy.alerts import Audio
import scanbuddy.scanner as scanner
from scanbuddy.logging import DuplicateFilter

logger = logging.getLogger(__name__)
logger.addFilter(DuplicateFilter())

class Plugin:
    def __init__(self, db, metadata, params):
        self._db = db
        self._metadata = metadata
        self._params = params
        self._audio = Audio()

    def run(self):
        errors = list()
        Scanner = None
        files = os.listdir(self._db)
        num_files = len(files)
        for f in files:
            fullfile = os.path.join(self._db, f)
            ds = pydicom.read_file(fullfile)
            name = ds.PatientName
            series = ds.SeriesNumber
            description = ds.SeriesDescription
            ds.num_files = num_files
            if not Scanner:
                Scanner = scanner.get(ds)
            ds = Scanner(ds)
            for key,expected in iter(self._params.items()):
                # check if expected value is a regex
                regex = re.match('regex\((.*)\)', str(expected))
                if regex:
                    expected = regex.group(1).strip()
                actual = getattr(ds, key)()
                try:
                    if regex:
                        assert re.match(expected, actual) != None
                    else:
                        assert actual == expected
                except AssertionError as e:
                    if (series, key) in errors:
                        continue
                    errors.append((series, key))
                    message = f'{name}::{description}::{series} - {key} - expected "{expected}" but found "{actual}"'
                    logger.error(colored(message, 'red', attrs=['bold', 'blink']))
                    self._audio.error()
            
