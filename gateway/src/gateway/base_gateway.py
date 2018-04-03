from threading import Lock

from gateway.src.account.account_listener import AccountTransfersListener


class GatewaySyncState:
    _active = False
    _interrupted = False
    _lock = Lock()

    @property
    def active(self):
        with self._lock:
            return self._active

    @active.setter
    def active(self, value):
        with self._lock:
            self._active = value

    @property
    def interrupted(self):
        with self._lock:
            return self._interrupted

    @interrupted.setter
    def interrupted(self, value):
        with self._lock:
            self._interrupted = value


class BaseGateway(object):
    TRANSACTION_MODEL = None

    def __init__(self):
        self.transfers_provider = self._create_transfers_provider()
        self.transfer_listener = AccountTransfersListener(self.transfers_provider)
        self.transfers_handler = self._create_transfers_handler()
        self.transfer_listener.add_handler(self.transfers_handler)
        self.gateway_sync_state = GatewaySyncState()

    def sync_database(self):
        self.gateway_sync_state.active = True
        self.transfer_listener.transfers_provider.fetch_all_transactions()

        txs = self.TRANSACTION_MODEL.objects.all()
        self.transfers_handler.sync(txs, lambda: self.gateway_sync_state.active)

        non_processed_txs = txs.filter(error=False, closed=False)
        if non_processed_txs.count():
            self.transfers_handler.handle(non_processed_txs, lambda: self.gateway_sync_state.active)
        self.gateway_sync_state.active = False

    def _create_transfers_provider(self):
        raise NotImplementedError()

    def _create_transfers_handler(self):
        raise NotImplementedError()

    def start(self):
        self.sync_database()

        if not self.gateway_sync_state.interrupted:
            self.transfer_listener.start()

    def stop(self):
        self.gateway_sync_state.active = False
        self.gateway_sync_state.interrupted = True
        self.transfer_listener.stop()

    @property
    def active(self):
        return self.transfer_listener.active or self.gateway_sync_state.active
