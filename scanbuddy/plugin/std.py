import os
import pydicom
import logging
import matplotlib
import matplotlib.pyplot as plt
from termcolor import colored
from multiprocessing import Process

logger = logging.getLogger(__name__)

class Plugin:
    def __init__(self, db, params, series=None):
        self._db = db
        self._params = params
        self._series = series

    def run(self):
        logger.info('running std plugin')
        errors = list()
        for f in os.listdir(self._db):
            fname = os.path.join(self._db, f)
            ds = pydicom.read_file(fname)
            series = ds.SeriesNumber
            instance = ds.InstanceNumber
            arr = ds.pixel_array
            contrast = arr.std()
            for op,expected in iter(self._params.items()):
                if op == 'lt':
                    if contrast < expected:
                        if (series, instance) in errors:
                            continue
                        errors.append((series, instance))
                        message = f'- series {series} - instance {instance} std {contrast:.2f} < {expected}'
                        logger.error(colored(message, 'red', attrs=['bold', 'blink']))
                        self.plot(arr)

    def plot(self, arr):
        p = Process(target=self._plot, args=(arr,))
        p.start()

    def _plot(self, arr):
        plt.imshow(arr, cmap='gray')
        plt.show()
