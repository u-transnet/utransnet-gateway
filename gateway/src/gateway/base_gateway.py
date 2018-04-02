from gateway.src.account.account_listener import AccountTransfersListener


class BaseGateway(object):
    TRANSACTION_MODEL = None

    def __init__(self):
        self.transfers_provider = self._create_transfers_provider()
        self.transfer_listener = AccountTransfersListener(self.transfers_provider)
        self.transfers_handler = self._create_transfers_handler()
        self.transfer_listener.add_handler(self.transfers_handler)

        self.sync_database()

    def sync_database(self):
        self.transfer_listener.transfers_provider.fetch_all_transactions()
        self.transfers_handler.sync(self.TRANSACTION_MODEL.objects.all())

    def _create_transfers_provider(self):
        raise NotImplementedError()

    def _create_transfers_handler(self):
        raise NotImplementedError()

    def start(self):
        self.transfer_listener.start()

    def stop(self):
        self.transfer_listener.stop()

    @property
    def active(self):
        return self.transfer_listener.active