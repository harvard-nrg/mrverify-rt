import os
import re
import time
import pydicom
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')
import urllib.parse

class Plugin:
    def __init__(self, app, db, metadata, params, save_dirname='~/Desktop/images'):
        self.app = app
        self.critical = (False, None, False)
        self._db = db
        self._metadata = metadata
        self._params = params if params else dict()
        save_dirname = os.path.expanduser(save_dirname)
        self._save_dirname = os.path.join(save_dirname, 'std')
        os.makedirs(self._save_dirname, exist_ok=True)

    def run(self):
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
                bsod = params.get('bsod', False)
                if op == 'lt' and contrast < expecting:
                    if params.get('append_coil_string', False):
                        coil_str = ds[(0x0051, 0x100f)].value
                        instance = f'{instance}[{coil_str}]'
                    self.critical = (True, message, bsod)
                    details = f'{name}, scan {series}, {description}, instance {instance} has std {contrast:.2f} < {expecting}'
                    self.app.call_from_thread(
                        self.app.logger.error,
                        f'[bold red blink]{details}[/]'
                    )
                    self.plot(ds.pixel_array, instance=instance)

    def plot(self, arr, **kwargs):
        name = self._metadata['PatientName'].value
        series = self._metadata['SeriesNumber'].value
        description = self._metadata['SeriesDescription'].value
        instance = kwargs.get('instance') or self._metadata['InstanceNumber'].value
        matplotlib.rcParams['toolbar'] = 'None'
        plt.clf()
        fig = plt.figure(f'{name}')
        plt.title(f'{name}\n{description}')
        plt.gca().set_xticks([])
        plt.gca().set_yticks([])
        plt.gca().set_xlabel(f'series {series} - instance {instance}\nlow σ')
        plt.imshow(arr, cmap='gray')
        legal = re.compile('[^a-zA-Z0-9]')
        ses = legal.sub('', str(name))
        basename = f'ses-{ses}_series-{series}_instance-{instance}_std.png'
        fname = os.path.join(
            self._save_dirname,
            basename
        )
        plt.savefig(fname)
        url = urllib.parse.quote(f'{fname}')
        self.app.call_from_thread(
            self.app.logger.info,
            f'[link=file://{url}]click here to view image[/link]'
        )
