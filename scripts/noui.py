#!/usr/bin/env python

import os
import shutil
import logging
import scanbuddy
import multiprocessing
from argparse import ArgumentParser
from pynetdicom import AE, evt, AllStoragePresentationContexts, _config

import scanbuddy.config as config
from scanbuddy.ingress import SeriesIngress

logger = logging.getLogger('scanbuddy')
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    datefmt='%b %d %H:%M:%S'
)
   
Pool = dict()

def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    parser.add_argument('--address', default='0.0.0.0')
    parser.add_argument('--port', default=11112, type=int)
    parser.add_argument('--ae-title', default='SCANBUDDY')
    parser.add_argument('--cache', default='~/.cache')
    parser.add_argument('--no-sound', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    logging.getLogger('scanbuddy').setLevel(logging.INFO)
    if args.verbose:
        logging.getLogger('scanbuddy').setLevel(logging.DEBUG)
    
    logger.info(f'Scan Buddy {scanbuddy.version()} is ready.')

    config.no_sound = args.no_sound

    args.cache = os.path.expanduser(args.cache)
    args.cache = os.path.join(args.cache, 'scanbuddy')
    if os.path.exists(args.cache):
        logger.info(f'clearing cache {args.cache}')
        shutil.rmtree(args.cache)

    # catchall for unknown SOP classes e.g., Siemens PhysioLog
    _config.UNRESTRICTED_STORAGE_SERVICE = True 

    ae = AE()
    ae.supported_contexts = AllStoragePresentationContexts
    logger.info(f'starting dicom receiver "{args.ae_title}" on {args.address}:{args.port}')
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
    if not ds.PatientName:
        ds.PatientName = 'Unknown'
    if key not in Pool:
        logger.info(f'receiving {ds.PatientName} scan {ds.SeriesNumber}')
        Pool[key] = SeriesIngress(conf, cache=cache)
        Pool[key].register_cleanup_callback(lambda: Pool.pop(key))
    ingressor = Pool[key]
    ingressor.save(ds)
    return 0x0000

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    main()
