import os
import re
import logging
import subprocess as sp
from multiprocessing import Process

import numpy as np
import nibabel as nib
import pydicom
import matplotlib
import matplotlib.pyplot as plt

from scanbuddy.timer import Timer
from scanbuddy.commons import which

logger = logging.getLogger('plugins.volreg')

class Plugin:
    def __init__(self, db, metadata, params, save_dirname='~/Desktop/images'):
        self._db = db
        self._metadata = metadata
        self._params = params if params else dict()
        save_dirname = os.path.expanduser(save_dirname)
        self._save_dirname = os.path.join(save_dirname, 'volreg')
        os.makedirs(self._save_dirname, exist_ok=True)

    def run(self):
        logger.info('running bold motion plugin')
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
        nii = os.path.join(self._db, 'bold.nii.gz')
        ds = nib.load(nii)
        dims = ds.header['dim'][0]
        if dims < 4:
            logger.info(f'series only has {dims} dimensions')
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

    def plot(self, arr):
        p = Process(
            target=self._plot,
            args=(arr,)
        ).start()

    def _plot(self, arr):
        name = self._metadata['PatientName'].value
        series = self._metadata['SeriesNumber'].value
        description = self._metadata['SeriesDescription'].value
        matplotlib.rcParams['toolbar'] = 'None'
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
        plt.show(block=False)
        plot_timeout = self._params.get('plot_timeout', 120)
        plt.pause(plot_timeout)
