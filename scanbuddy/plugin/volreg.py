import os
import re
import logging
import subprocess as sp
from multiprocessing import Process

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from scanbuddy.timer import Timer
from scanbuddy.commons import which

logger = logging.getLogger(__name__)

class Plugin:
    def __init__(self, db, params, series=None):
        self._db = db
        self._params = params
        self._series = series

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
        # plot motion parameters
        p = Process(target=self._plot, args=(arr,))
        p.start()

    def _plot(self, arr):      
        matplotlib.rc('lines', antialiased=True, linewidth=0.5)
        matplotlib.rc('legend', fontsize=10)
        # rotations subplot
        plt.subplot(211)
        plt.plot(arr[:, 0:3])
        plt.legend(['roll', 'pitch', 'yaw'])
        plt.title(f'Rotations - series {self._series}')
        plt.xlabel('Volumes (N)')
        plt.ylabel('radians')
        plt.autoscale(enable=True, axis='both', tight=True)
        # translations subplot
        plt.subplot(212)
        plt.plot(arr[:, 3:])
        plt.legend(['superior', 'left', 'posterior'])
        plt.title(f'Displacements - series {self._series}')
        plt.xlabel('Volumes (N)')
        plt.ylabel('mm')
        plt.autoscale(enable=True, axis='both', tight=True)
        plt.subplots_adjust(hspace=.5)
        plt.show()
      
