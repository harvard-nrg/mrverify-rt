import os
import re
import yaml
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, filename):
        self._filename = filename
        self._content = self._parse_file()

    def _parse_file(self):
        logger.debug(f'parsing {self._filename}')
        with open(self._filename) as fo:
            return yaml.load(fo, Loader=yaml.FullLoader)

    def select(self, ds):
        for item in self._content:
            match = True
            for key,expected in iter(item['selector'].items()):
                regex = re.match('regex\((.*)\)', str(expected))
                if regex:
                    expected = regex.group(1).strip()
                f = getattr(ds, key)
                actual = f()
                if regex:
                    compare = re.match(expected, actual)
                else:
                    compare = (expected == actual)
                match = match and compare
            if match:
                return item['plugins']
        return dict()
