import time
import logging

logger = logging.getLogger(__name__)

class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            logger.info('[%s]' % self.name,)
        logger.info('Elapsed: %s' % (time.time() - self.tstart))
