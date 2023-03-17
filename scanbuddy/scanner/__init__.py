import logging

from scanbuddy.scanner.siemens.prisma import Prisma
from scanbuddy.scanner.siemens.skyra import Skyra

logger = logging.getLogger(__name__)

mapping = {
   ('SIEMENS', 'Skyra'): Skyra,
   ('SIEMENS', 'Prisma'): Prisma,
   ('SIEMENS', 'Prisma_fit'): Prisma
}

def get(ds):
    make_model = (
        ds.Manufacturer,
        ds.ManufacturerModelName
    )
    if make_model in mapping:
        return mapping[make_model]
    raise UnrecognizedScannerError(make_model)

class UnrecognizedScannerError(Exception):
    pass

