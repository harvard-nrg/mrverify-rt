import logging

from scanbuddy.scanner.siemens import Siemens

logger = logging.getLogger(__name__)

class Skyra(Siemens):
    @classmethod
    def check_model(cls, model):
        if model in ['Skyra']:
            return True
        return False
 
