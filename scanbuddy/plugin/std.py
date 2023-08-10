import os
import re
import pydicom
import logging
import matplotlib
import multiprocessing as m
import matplotlib.pyplot as plt
from termcolor import colored
from multiprocessing import Process

logger = logging.getLogger(__name__)

class Plugin:
    def __init__(self, db, metadata, params, save_dirname='~/Desktop/images'):
        self._db = db
        self._metadata = metadata
        self._params = params if params else dict()
        save_dirname = os.path.expanduser(save_dirname)
        self._save_dirname = os.path.join(save_dirname, 'std')
        os.makedirs(self._save_dirname, exist_ok=True)

    def run(self):
        logger.info('running std plugin')
        for f in os.listdir(self._db):
            fname = os.path.join(self._db, f)
            ds = pydicom.read_file(fname)
            name = ds.PatientName
            series = ds.SeriesNumber
            description = ds.SeriesDescription
            instance = ds.InstanceNumber
            self._metadata['InstanceNumber'].value = instance
            contrast = ds.pixel_array.std()
            for op,params in iter(self._params.items()):
                expecting = params['expecting']
                message = params.get('message', None)
                if op == 'lt' and contrast < expecting:
                    if message:
                        logger.error(colored(message, 'red', attrs=['bold', 'blink']))
                    details = f'scan {series} - {description} - instance {instance} has std {contrast:.2f} < {expecting}'
                    logger.error(colored(details, 'red', attrs=['bold', 'blink']))
                    self.plot(ds.pixel_array)

    def plot(self, arr):
        p = Process(
            target=self._plot,
            args=(arr,)
        ).start()
    
    def _plot(self, arr):
        name = self._metadata['PatientName'].value
        series = self._metadata['SeriesNumber'].value
        description = self._metadata['SeriesDescription'].value
        instance = self._metadata['InstanceNumber'].value
        matplotlib.rcParams['toolbar'] = 'None'
        fig = plt.figure(f'{name}')
        plt.title(f'{name}\n{description}')
        plt.gca().set_xticks([])
        plt.gca().set_yticks([])
        plt.gca().set_xlabel(f'series {series} - instance {instance}\nlow σ')
        plt.imshow(arr, cmap='gray')
        legal = re.compile('[^a-zA-Z0-9]')
        ses = legal.sub('', str(name))
        fname = os.path.join(
            self._save_dirname,
            f'ses-{ses}_series-{series}_instance-{instance}_std.png'
        )
        plt.savefig(fname)
        plt.show(block=False)
        plot_timeout = self._params.get('plot_timeout', 120)
        plt.pause(plot_timeout)
