import logging

from scanbuddy.scanner.siemens import Siemens

logger = logging.getLogger(__name__)

class Prisma(Siemens):
    @classmethod
    def check_model(cls, model):
        if model in ['Prisma', 'Prisma_fit']:
            return True
        return False

