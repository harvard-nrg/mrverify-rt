import sys
import logging
from textual.widgets import RichLog
from pynetdicom import (
    AE, evt, ALL_TRANSFER_SYNTAXES, 
    AllStoragePresentationContexts, _config
)
from pathlib import Path
from scanbuddy.ingress import SeriesIngress

logger = logging.getLogger('scanbuddy.cstore')

class CStore:
    _config.UNRESTRICTED_STORAGE_SERVICE = True

    def __init__(self, app):
        self.app = app

    def run(self):
        address = self.app.args.address
        port = self.app.args.port
        ae_title = self.app.args.ae_title
        max_pdu_size = self.app.args.max_pdu_size
        self.app.logger.info(f'starting receiver {ae_title} on {address}:{port}')
        ae = AE()
        ae.maximum_pdu_size = max_pdu_size
        ae.supported_contexts = AllStoragePresentationContexts
        handlers = [
            (
                evt.EVT_C_STORE, 
                handle_store,
                [
                    self.app,
                    self.app.args.config,
                    self.app.args.cache
                ]
            )
        ]
        ae.start_server(
            (
                self.app.args.address,
                self.app.args.port
            ),
            ae_title=self.app.args.ae_title,
            evt_handlers=handlers,
            block=False
        )

Pool = dict()

def handle_store(event, app, conf, cache):
    ds = event.dataset
    ds.file_meta = event.file_meta
    key = f'{ds.StudyInstanceUID}.{ds.SeriesNumber}'
    if not ds.PatientName:
        ds.PatientName = 'Unknown'
    if key not in Pool:
        app.logger.info(f'receiving {ds.PatientName} scan {ds.SeriesNumber}')
        Pool[key] = SeriesIngress(app, conf, cache=cache)
        Pool[key].register_cleanup_callback(lambda: Pool.pop(key))
    ingressor = Pool[key]
    ingressor.save(ds)
    return 0x0000

