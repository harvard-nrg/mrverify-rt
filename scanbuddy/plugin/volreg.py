import os
import re
from glob import glob
import subprocess as sp
import numpy as np
import nibabel as nib
import pydicom
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import urllib.parse
from scanbuddy.timer import Timer
from scanbuddy.commons import which
from rich.panel import Panel
from rich.text import Text
import plotext as plx

class Plugin:
    def __init__(self, app, db, metadata, params, save_dirname='~/Desktop/images'):
        self.app = app
        self.critical = (False, None, False)
        self._db = db
        self._metadata = metadata
        self._params = params if params else dict()
        save_dirname = os.path.expanduser(save_dirname)
        self._save_dirname = os.path.join(save_dirname, 'volreg')
        os.makedirs(self._save_dirname, exist_ok=True)

    def run(self):
        series = self._metadata['SeriesNumber'].value
        self.app.call_from_thread(
            self.app.logger.info,
            f'running bold motion plugin on series {series}'
        )
        # check installed dependencies
        for x in ['dcm2niix', '3dvolreg']:
            if not which(x):
                raise FileNotFoundError(f'could not find {x}')
        # convert DICOM to NIFTI
        cmd = [
            'dcm2niix',
            '-b', 'y',
            '-z', 'y',
            '-f', 'bold',
            '-o', self._db,
            self._db
        ]
        with Timer('dcm2niix'):
            _ = sp.check_output(cmd, stderr=sp.STDOUT)
        # find single nifti file or multiecho nifti
        nii = self.find_nii()
        if not nii:
            self.app.call_from_thread(
                self.app.logger.warning,
                f'could not find a nifti for series {series}'
            )
            return
        ds = nib.load(nii)
        dims = ds.header['dim'][0]
        if dims < 4:
            self.app.call_from_thread(
                self.app.logger.info,
                f'series only has {dims} dimensions'
            )
            return
        # estimate motion parameters
        mocopar = os.path.join(self._db, 'moco.par')
        cmd = [
            '3dvolreg',
            '-linear',
            '-1Dfile', mocopar,
            '-x_thresh', '10',
            '-rot_thresh', '10',
            '-prefix', 'NULL',
            nii
        ]
        with Timer('3dvolreg'):
            _ = sp.check_output(cmd, stderr=sp.STDOUT)
        data = list()
        with open(mocopar, 'r') as fo:
            for line in fo:
                row = re.split('\s+', line.strip())
                row = list(map(float, row))
                data.append(row)
        arr = np.array(data)
        self.plot(arr)

    def find_nii(self):
        # look for a single nifti file
        nii = os.path.join(self._db, 'bold.nii.gz')
        if os.path.exists(nii):
           return nii
        # look for second echo from multiecho scan
        nii = os.path.join(self._db, 'bold_e2.nii.gz')
        if os.path.exists(nii):
            return nii
        return None

    def plot(self, arr):
        name = self._metadata['PatientName'].value
        series = self._metadata['SeriesNumber'].value
        description = self._metadata['SeriesDescription'].value
        matplotlib.rcParams['toolbar'] = 'None'
        plt.clf()
        fig = plt.figure(f'{name}')
        plt.style.use('bmh')
        # rotations subplot
        plt.subplot(211)
        plt.plot(arr[:, 0:3])
        plt.legend(['roll', 'pitch', 'yaw'], loc='lower right')
        plt.title(f'Rotations - series {series}')
        plt.xlabel('Volumes (N)')
        plt.ylabel('degrees')
        plt.autoscale(enable=True, axis='both', tight=True)
        # translations subplot
        plt.subplot(212)
        plt.plot(arr[:, 3:])
        plt.legend(['superior', 'left', 'posterior'], loc='lower right')
        plt.title(f'Displacements - series {series}')
        plt.xlabel('Volumes (N)')
        plt.ylabel('mm')
        plt.autoscale(enable=True, axis='both', tight=True)
        plt.subplots_adjust(hspace=.5)
        legal = re.compile('[^a-zA-Z0-9]')
        ses = legal.sub('', str(name))
        fname = os.path.join(
            self._save_dirname,
            f'ses-{ses}_series-{series}_volreg.png'
        )
        plt.savefig(fname)
        url = urllib.parse.quote(f'{fname}')
        self.app.call_from_thread(
            self.app.logger.info,
            f'[link=file://{url}]click here to view image[/link]'
        )
        # convert figure to text and print to the console
        plx.from_matplotlib(fig)
        plx.subplot(1, 1).plotsize(70, 20)
        plx.subplot(1, 1).theme('retro')
        plx.subplot(2, 1).plotsize(70, 20)
        plx.subplot(2, 1).xlabel('Volumes (N)')
        plx.subplot(2, 1).theme('retro')
        txt = Text.from_ansi(plx.build())
        self.app.call_from_thread(
            self.app.logger.write,
            Panel(txt, expand=False)
        )
