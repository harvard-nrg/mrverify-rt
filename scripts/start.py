#!/usr/bin/env python

import os
import shutil
import logging
from argparse import ArgumentParser
from pynetdicom import AE, evt, AllStoragePresentationContexts, _config

from scanbuddy.ingress import SeriesIngress

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Pool = dict()

def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    parser.add_argument('--address', default='0.0.0.0')
    parser.add_argument('--port', default=11112, type=int)
    parser.add_argument('--ae-title', default='SCANBUDDY')
    parser.add_argument('--cache', default='~/.cache/scanbuddy')
    args = parser.parse_args()

    logging.getLogger('pynetdicom').setLevel(logging.ERROR)

    args.cache = os.path.expanduser(args.cache)
    if os.path.exists(args.cache):
        logger.info(f'cleaning up cache {args.cache}')
        shutil.rmtree(args.cache)

    # catchall for unknown SOP classes e.g., Siemens PhysioLog
    _config.UNRESTRICTED_STORAGE_SERVICE = True 

    ae = AE()
    ae.supported_contexts = AllStoragePresentationContexts
    logger.info(f'starting dicom receiver {args.ae_title} on {args.address}:{args.port}')
    handlers = [(evt.EVT_C_STORE, handle_store, [args.config, args.cache])]
    ae.maximum_pdu_size = 0
    ae.start_server(
        (args.address, args.port),
        ae_title=args.ae_title, 
        evt_handlers=handlers
    )

def handle_store(event, conf, cache):
    ds = event.dataset
    ds.file_meta = event.file_meta
    key = f'{ds.StudyInstanceUID}.{ds.SeriesNumber}'
    if key not in Pool:
        logger.info(f'receiving files for series {ds.SeriesNumber}')
        Pool[key] = SeriesIngress(conf, cache=cache)
    ingressor = Pool[key]
    ingressor.save(ds)
    return 0x0000

if __name__ == '__main__':
    main()
