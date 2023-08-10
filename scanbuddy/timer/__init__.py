import time
import logging

logger = logging.getLogger(__name__)

class Timer(object):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        elapsed = time.time() - self.tstart
        logger.debug(f'{self.name} elapsed: {elapsed}')
