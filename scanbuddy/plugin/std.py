import os
import re
import pydicom
import logging
import matplotlib
import matplotlib.pyplot as plt
from termcolor import colored
from multiprocessing import Process

logger = logging.getLogger(__name__)

class Plugin:
    def __init__(self, db, params, series=None, save_dirname='~/Desktop/images'):
        self._db = db
        self._params = params
        self._series = series
        self._save_dirname = os.path.expanduser(save_dirname)
        os.makedirs(self._save_dirname, exist_ok=True)

    def run(self):
        logger.info('running std plugin')
        errors = list()
        for f in os.listdir(self._db):
            fname = os.path.join(self._db, f)
            ds = pydicom.read_file(fname)
            name = ds.PatientName
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
                        self.plot(arr, name, series, instance)

    def plot(self, arr, name, series, instance):
        p = Process(target=self._plot, args=(arr, name, series, instance))
        p.start()

    def _plot(self, arr, name, series, instance):
        matplotlib.rcParams['toolbar'] = 'None'
        fig = plt.figure(f'{name}')
        plt.title(f'{name} - series {series}, instance {instance}')
        plt.axis('off')
        plt.imshow(arr, cmap='gray')
        legal = re.compile('[^a-zA-Z0-9]')
        ses = legal.sub('', str(name))
        fname = os.path.join(
            self._save_dirname,
            f'ses-{ses}_series-{series}_instance-{instance}_std.png'
        )
        plt.savefig(fname)
        plt.show(block=False)
        plt.pause(60) # display figure for 5 minutes
        plt.close()

